"""HackathonAgent — plain browse/filter layer for the Hackathon Finder.

No eligibility scoring, no matching logic, no profile dependency.
This is a pure browse feature: fetch all active hackathons, apply
optional filters, sort by registration deadline, return paginated results.

Filter dimensions supported:
  - mode         : "online" | "offline" | "hybrid"
  - source       : platform slug  (e.g. "devfolio", "mlh")
  - theme        : substring match against themes list
  - prize_min    : minimum prize pool (integer rupees)
  - location     : substring match against location field
  - deadline_days: only show hackathons whose reg deadline is within N days
  - query        : substring search across title + organizer + themes
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Hackathon

logger = logging.getLogger(__name__)


class HackathonAgent:
    """Stateless browse/filter agent for hackathon listings."""

    def list(
        self,
        db: Session,
        *,
        query:         Optional[str] = None,
        mode:          Optional[str] = None,
        source:        Optional[str] = None,
        theme:         Optional[str] = None,
        prize_min:     Optional[int] = None,
        location:      Optional[str] = None,
        deadline_days: Optional[int] = None,
        limit:         int = 60,
        offset:        int = 0,
    ) -> dict:
        """Return filtered hackathon listings.

        Returns
        -------
        dict with keys:
          items  — list of Hackathon ORM objects
          total  — count before pagination
        """
        q = db.query(Hackathon).filter_by(is_active=True)

        # ── hard filters ──────────────────────────────────────────────────────
        if mode:
            q = q.filter(Hackathon.mode == mode.lower())

        if source:
            q = q.filter(Hackathon.source == source.lower())

        if prize_min is not None and prize_min > 0:
            q = q.filter(Hackathon.prize_pool >= prize_min)

        if deadline_days is not None:
            cutoff = date.today() + timedelta(days=deadline_days)
            q = q.filter(
                Hackathon.registration_deadline != None,
                Hackathon.registration_deadline <= cutoff,
                Hackathon.registration_deadline >= date.today(),
            )

        # ── soft filters (Python-side, post-fetch) ────────────────────────────
        # These are applied after the DB query because SQLite/SQLAlchemy JSON
        # array contains-checks are unreliable cross-database.
        all_rows: list[Hackathon] = q.all()

        if location:
            loc_lower = location.lower()
            all_rows = [
                h for h in all_rows
                if h.location and loc_lower in h.location.lower()
            ]

        if theme:
            theme_lower = theme.lower()
            all_rows = [
                h for h in all_rows
                if h.themes and any(theme_lower in t.lower() for t in h.themes)
            ]

        if query:
            q_lower = query.lower()
            def _matches(h: Hackathon) -> bool:
                haystack = " ".join(filter(None, [
                    h.title or "",
                    h.organizer or "",
                    " ".join(h.themes or []),
                    h.location or "",
                ])).lower()
                return q_lower in haystack
            all_rows = [h for h in all_rows if _matches(h)]

        # ── sort: soonest registration deadline first; None deadlines last ────
        def _sort_key(h: Hackathon):
            if h.registration_deadline is None:
                return date(9999, 12, 31)
            return h.registration_deadline

        all_rows.sort(key=_sort_key)

        total = len(all_rows)
        paginated = all_rows[offset : offset + limit]

        return {"items": paginated, "total": total}
