"""Hackathon ingestion pipeline.

Loads all 8 hackathon connectors (4 live + 4 dummy), runs fetch(), and
upserts results into the hackathons table.  Called from the main
run_ingestion() in pipeline.py and from the daily Celery task.

Live scrapers (return [] gracefully on failure — pipeline never aborts):
  - UnstopHackathonConnector   (Playwright, unstop.com/hackathons)
  - DevfolioConnector          (Playwright + SSR, devfolio.co/hackathons)
  - MLHConnector               (Playwright + SSR, mlh.io/seasons/2027/events)
  - LablabConnector            (Playwright + SSR, lablab.ai/event)

Dummy connectors (instant static data, no network calls):
  - DevpostHackathonConnector
  - HackerEarthHackathonConnector
  - HackIndiaConnector
  - Hack2SkillConnector
"""

from __future__ import annotations

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.db.models import Hackathon

logger = logging.getLogger(__name__)


# ── connector registry ────────────────────────────────────────────────────────

def _load_hackathon_connectors() -> list:
    connectors = []

    # ── Live scrapers ──────────────────────────────────────────────────────────
    _live = [
        ("app.ingestion.connectors.unstop_hackathon_sync", "UnstopHackathonConnector"),
        ("app.ingestion.connectors.devfolio_sync",         "DevfolioConnector"),
        ("app.ingestion.connectors.mlh_sync",              "MLHConnector"),
        ("app.ingestion.connectors.lablab_sync",           "LablabConnector"),
    ]
    for mod_path, cls_name in _live:
        try:
            import importlib
            mod = importlib.import_module(mod_path)
            connector = getattr(mod, cls_name)()
            connectors.append(connector)
            logger.info(f"HackathonPipeline: loaded {cls_name} (live scraper)")
        except Exception as exc:
            logger.warning(f"HackathonPipeline: could not load {cls_name} — {exc}")

    # ── Dummy data connectors ──────────────────────────────────────────────────
    _dummy = [
        ("app.ingestion.connectors.devpost_hackathon",      "DevpostHackathonConnector"),
        ("app.ingestion.connectors.hackerearth_hackathon",  "HackerEarthHackathonConnector"),
        ("app.ingestion.connectors.hackindia_hackathon",    "HackIndiaConnector"),
        ("app.ingestion.connectors.hack2skill_hackathon",   "Hack2SkillConnector"),
    ]
    for mod_path, cls_name in _dummy:
        try:
            import importlib
            mod = importlib.import_module(mod_path)
            connector = getattr(mod, cls_name)()
            connectors.append(connector)
            logger.info(f"HackathonPipeline: loaded {cls_name} (dummy data)")
        except Exception as exc:
            logger.warning(f"HackathonPipeline: could not load {cls_name} — {exc}")

    return connectors


HACKATHON_CONNECTORS = _load_hackathon_connectors()


# ── upsert helper ─────────────────────────────────────────────────────────────

def _deactivate_expired(db: Session) -> int:
    """Set is_active=False on stale hackathon rows.

    A row is stale if:
      - its registration_deadline is before today, OR
      - its start_date is in the past (catches old-season scrape artifacts
        that were given a fallback deadline of 'today+1').

    Returns the count of rows deactivated.
    """
    from sqlalchemy import or_
    today = date.today()
    expired = (
        db.query(Hackathon)
        .filter(Hackathon.is_active == True)
        .filter(
            or_(
                Hackathon.registration_deadline < today,
                Hackathon.start_date < today,
            )
        )
        .all()
    )
    for h in expired:
        h.is_active = False
    if expired:
        db.commit()
        logger.info(f"HackathonPipeline: deactivated {len(expired)} expired hackathons")
    return len(expired)


def _upsert_hackathon(db: Session, raw) -> tuple[Hackathon, bool]:
    """Insert or update one hackathon row.

    Returns (Hackathon, is_new).
    """
    existing = (
        db.query(Hackathon)
        .filter_by(source=raw.source, external_id=raw.external_id)
        .first()
    )

    data = dict(
        source=raw.source,
        external_id=raw.external_id,
        title=(raw.title or "").strip(),
        organizer=(raw.organizer or "").strip() or None,
        mode=(raw.mode or "online").lower(),
        location=(raw.location or "").strip() or None,
        team_size=(raw.team_size or "").strip() or None,
        prize_pool=int(raw.prize_pool or 0),
        registration_deadline=raw.registration_deadline,
        start_date=raw.start_date,
        end_date=raw.end_date,
        themes=raw.themes or [],
        apply_link=(raw.apply_link or "").strip() or None,
        posted_date=raw.posted_date,
        is_active=True,
        last_synced_at=datetime.utcnow(),
    )

    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)
        return existing, False
    else:
        hackathon = Hackathon(**data)
        db.add(hackathon)
        return hackathon, True


# ── public entry point ────────────────────────────────────────────────────────

def run_hackathon_ingestion(db: Session) -> dict:
    """Run all hackathon connectors and sync to the hackathons table.

    Returns a stats dict that matches the format used by run_ingestion()
    in pipeline.py so the Celery task can merge them.
    """
    stats: dict = {
        "inserted": 0,
        "updated": 0,
        "errors": 0,
        "sources": {},
        "completed_at": None,
    }

    # Deactivate any hackathon whose registration deadline has already passed.
    # This cleans up stale rows from previous scrape runs (e.g. old season
    # archives) so they stop appearing in the UI immediately.
    try:
        deactivated = _deactivate_expired(db)
        stats["deactivated"] = deactivated
    except Exception as exc:
        logger.warning(f"HackathonPipeline: deactivate_expired failed — {exc}")
        stats["deactivated"] = 0

    for connector in HACKATHON_CONNECTORS:
        source_stats: dict = {"fetched": 0, "inserted": 0, "updated": 0}
        try:
            raw_items = connector.fetch()
            source_stats["fetched"] = len(raw_items)

            for raw in raw_items:
                hackathon, is_new = _upsert_hackathon(db, raw)
                db.flush()
                if is_new:
                    stats["inserted"] += 1
                    source_stats["inserted"] += 1
                else:
                    stats["updated"] += 1
                    source_stats["updated"] += 1

            db.commit()
            logger.info(
                f"HackathonPipeline [{connector.source_id}]: "
                f"fetched={source_stats['fetched']} "
                f"inserted={source_stats['inserted']} "
                f"updated={source_stats['updated']}"
            )

        except Exception as exc:
            logger.exception(
                "HackathonPipeline: ingestion failed for %s", connector.source_id
            )
            stats["errors"] += 1
            source_stats["error"] = str(exc)
            db.rollback()

        stats["sources"][connector.source_id] = source_stats

    stats["completed_at"] = datetime.utcnow().isoformat()
    return stats
