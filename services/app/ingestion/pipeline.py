import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Opportunity
from app.ingestion.normalizer import normalize, normalize_internship, upsert_opportunity
from app.knowledge.hybrid_rag import HybridRAG

logger = logging.getLogger(__name__)

# ── Scholarship connectors ────────────────────────────────────────────────────
CONNECTORS = []
try:
    from app.ingestion.connectors import NSPConnector, MahaDBTConnector, MySchemeConnector
    CONNECTORS = [NSPConnector(), MahaDBTConnector(), MySchemeConnector()]
except ImportError:
    logger.warning("Scholarship connectors not found")

# ── Internship connectors ─────────────────────────────────────────────────────
# Internshala: live Playwright scraper (or seed fallback)
# Indeed, Naukri, Wellfound, Unstop: static dummy data — no network calls

def _load_internship_connectors():
    connectors = []

    # 1. Internshala — live Playwright scraper; falls back to seeder if unavailable
    try:
        from app.ingestion.connectors.internshala_sync import InternshalaLiveConnector
        connectors.append(InternshalaLiveConnector())
        logger.info("Pipeline: loaded InternshalaLiveConnector (live)")
    except ImportError:
        try:
            from app.ingestion.connectors.seed_connectors import InternshalaSeeder
            connectors.append(InternshalaSeeder())
            logger.warning("Pipeline: Internshala live unavailable — using seeder")
        except ImportError:
            logger.warning("Pipeline: no Internshala connector found")

    # 2–5. Dummy connectors — instant static data, no network calls
    for mod, cls in [
        ("app.ingestion.connectors.indeed_connector",    "IndeedConnector"),
        ("app.ingestion.connectors.naukri_connector",    "NaukriConnector"),
        ("app.ingestion.connectors.wellfound_connector", "WellfoundConnector"),
        ("app.ingestion.connectors.unstop_connector",    "UnstopConnector"),
    ]:
        try:
            import importlib
            module = importlib.import_module(mod)
            connector = getattr(module, cls)()
            connectors.append(connector)
            logger.info(f"Pipeline: loaded {cls} (dummy data)")
        except Exception as exc:
            logger.warning(f"Pipeline: could not load {cls} — {exc}")

    return connectors


INTERNSHIP_CONNECTORS = _load_internship_connectors()


def run_ingestion(db: Session) -> dict:
    """Run scholarship + internship connectors and sync to DB + vector store."""
    rag   = HybridRAG()
    stats = {"inserted": 0, "updated": 0, "errors": 0, "sources": {}}

    # ── Scholarships ──────────────────────────────────────────────────────────
    for connector in CONNECTORS:
        source_stats = {"fetched": 0, "synced": 0}
        try:
            raw_items = connector.fetch()
            source_stats["fetched"] = len(raw_items)
            for raw in raw_items:
                data = normalize(raw)
                existing = db.query(Opportunity).filter_by(
                    source=data["source"], external_id=data["external_id"]
                ).first()
                opp = upsert_opportunity(db, data)
                db.flush()
                rag.index_opportunity(opp)
                stats["updated" if existing else "inserted"] += 1
                source_stats["synced"] += 1
            db.commit()
            stats["sources"][connector.source_id] = source_stats
        except Exception as exc:
            logger.exception("Scholarship ingestion failed for %s", connector.source_id)
            stats["errors"] += 1
            stats["sources"][connector.source_id] = {"error": str(exc)}
            db.rollback()

    # ── Internships ───────────────────────────────────────────────────────────
    for connector in INTERNSHIP_CONNECTORS:
        source_stats = {"fetched": 0, "synced": 0}
        try:
            raw_items = connector.fetch()
            source_stats["fetched"] = len(raw_items)
            for raw in raw_items:
                data = normalize_internship(raw)
                existing = db.query(Opportunity).filter_by(
                    source=data["source"], external_id=data["external_id"]
                ).first()
                opp = upsert_opportunity(db, data)
                db.flush()
                rag.index_opportunity(opp)
                stats["updated" if existing else "inserted"] += 1
                source_stats["synced"] += 1
            db.commit()
            stats["sources"][connector.source_id] = source_stats
        except Exception as exc:
            logger.exception("Internship ingestion failed for %s", connector.source_id)
            stats["errors"] += 1
            stats["sources"][connector.source_id] = {"error": str(exc)}
            db.rollback()

    stats["completed_at"] = datetime.utcnow().isoformat()
    return stats
