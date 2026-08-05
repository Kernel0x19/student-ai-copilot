from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import (
    Application, ApplicationState, Opportunity, OpportunityCategory, StudentProfile,
)
from app.intelligence.recommendation import (
    apply_feedback_learning, compute_match_score, compute_readiness_score,
)
from app.knowledge.hybrid_rag import HybridRAG
from app.schemas import MatchResult, OpportunityResponse, RecommendationResponse
from app.workflow.engine import WorkflowEngine, build_checklist

logger = logging.getLogger(__name__)


# ─── small helpers ────────────────────────────────────────────────────────────

def _location_matches(opp: Opportunity, location_filter: str) -> bool:
    loc = ((opp.raw_data or {}).get("location") or "").lower()
    f   = location_filter.lower()
    return f in loc or "work from home" in loc or "remote" in loc or f == "remote"


def _work_type(opp: Opportunity) -> str:
    loc = ((opp.raw_data or {}).get("location") or "").lower()
    if "work from home" in loc or "remote" in loc:
        return "remote"
    if "hybrid" in loc:
        return "hybrid"
    return "onsite"


def _duration_months(opp: Opportunity) -> Optional[int]:
    dur = ((opp.raw_data or {}).get("duration") or "").lower()
    m = re.search(r"(\d+)\s*month", dur)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*week", dur)
    if m:
        return max(1, int(m.group(1)) // 4)
    return None


# ─── agent ────────────────────────────────────────────────────────────────────

class InternshipAgent:
    """Orchestration layer for internship recommendations.

    Internshala provides live data; other sources provide static dummy data.
    Uses source-balanced sampling so no single platform dominates the feed.
    """

    def __init__(self) -> None:
        self.rag = HybridRAG()
        self.workflow = WorkflowEngine()

    def recommend(
        self,
        db: Session,
        profile: StudentProfile | None,
        query: str | None = None,
        state: str | None = None,
        location: str | None = None,
        work_type: str | None = None,
        duration_max: int | None = None,
        stipend_min: int | None = None,
        source: str | None = None,
        limit: int = 30,
    ) -> RecommendationResponse:

        # Profile preferences are used to enrich the semantic query and boost
        # scores — they do NOT act as hard filters, so the full cross-platform
        # feed is always visible. Users can apply hard filters via the UI.
        prefs = (profile.preferences or {}) if profile else {}

        # 1. Fetch all active internships
        opportunities: list[Opportunity] = (
            db.query(Opportunity)
            .filter_by(category=OpportunityCategory.INTERNSHIP, is_active=True)
            .all()
        )

        # 2. State filter
        if state:
            opportunities = [
                o for o in opportunities
                if not o.state_filter or "ALL" in o.state_filter or state in o.state_filter
            ]

        # 3. Platform / source filter
        if source:
            opportunities = [o for o in opportunities if o.source.lower() == source.lower()]

        # 4. Hard filters
        if location or work_type or duration_max is not None or stipend_min is not None:
            filtered = []
            for o in opportunities:
                if location and not _location_matches(o, location):
                    continue
                if work_type and _work_type(o) != work_type.lower():
                    continue
                if duration_max is not None:
                    months = _duration_months(o)
                    if months is not None and months > duration_max:
                        continue
                if stipend_min is not None:
                    effective = o.amount_min or o.amount_max or 0
                    if effective < stipend_min:
                        continue
                filtered.append(o)
            opportunities = filtered

        # 5. Semantic search or source-balanced sampling
        if query:
            enriched = query
            if profile:
                parts = [query]
                if profile.stream:        parts.append(profile.stream)
                if profile.skills:        parts.extend((profile.skills or [])[:5])
                if isinstance(prefs.get("interests"), list):
                    parts.extend(prefs["interests"][:3])
                enriched = " ".join(parts)

            semantic = self.rag.semantic_search(enriched, limit=limit * 2, category="internship")
            id_order = {s["opportunity_id"]: s["score"] for s in semantic if s.get("opportunity_id")}
            if id_order:
                in_results  = sorted([o for o in opportunities if o.id in id_order],
                                     key=lambda o: id_order.get(o.id, 0), reverse=True)
                not_in      = [o for o in opportunities if o.id not in id_order]
                opportunities = in_results + not_in
            opportunities = opportunities[: limit * 3]
        else:
            # Source-balanced: take evenly from each platform so Internshala's
            # larger pool (100+ rows) doesn't crowd out dummy sources (5 rows each).
            buckets: dict[str, list] = defaultdict(list)
            for o in opportunities:
                buckets[o.source].append(o)
            n_sources  = max(len(buckets), 1)
            per_source = max(5, (limit * 3) // n_sources)
            balanced: list[Opportunity] = []
            for src_opps in buckets.values():
                balanced.extend(src_opps[:per_source])
            seen_ids = {o.id for o in balanced}
            for o in opportunities:
                if o.id not in seen_ids:
                    balanced.append(o)
            opportunities = balanced[: limit * 3]

        # 6. Score
        matches: list[MatchResult] = []
        for opp in opportunities:
            base, eligibility, reasons = compute_match_score(profile, opp)
            if profile:
                adjusted = apply_feedback_learning(profile, opp, base / 100.0, db)
                final    = min(adjusted * 100.0, 99.0)
            else:
                final = base
            matches.append(
                MatchResult(
                    opportunity=OpportunityResponse.model_validate(opp),
                    match_score=round(final, 1),
                    eligibility=eligibility,
                    reasons=reasons,
                )
            )

        matches.sort(key=lambda m: m.match_score, reverse=True)

        return RecommendationResponse(
            matches=matches[:limit],
            total=len(matches),
            readiness_score=compute_readiness_score(profile),
        )

    def start_application(
        self,
        db: Session,
        user_id: str,
        opportunity_id: str,
        profile: StudentProfile | None,
        saved: bool = False,
    ) -> Application:
        opp = db.query(Opportunity).filter_by(id=opportunity_id).first()
        if not opp:
            raise ValueError("Opportunity not found")

        existing = db.query(Application).filter_by(
            user_id=user_id, opportunity_id=opportunity_id
        ).first()
        if existing:
            if saved and not existing.saved:
                existing.saved = True
                db.commit()
            return existing

        base, eligibility, _ = compute_match_score(profile, opp)
        checklist = build_checklist(
            opp.documents_required or [],
            (profile.documents if profile else []) or [],
        )
        app = Application(
            user_id=user_id, opportunity_id=opportunity_id,
            state=ApplicationState.DISCOVERED, match_score=base,
            eligibility_result=eligibility, checklist=checklist,
            saved=saved, progress_pct=10,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        self.workflow.transition(db, app, ApplicationState.ELIGIBILITY_CHECK,
                                 "system", "system", "Started internship workflow")
        return self.workflow.auto_advance_eligibility(db, app, eligibility)
