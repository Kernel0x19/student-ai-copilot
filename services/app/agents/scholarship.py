from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.db.models import Application, ApplicationState, Notification, Opportunity, OpportunityCategory, StudentProfile
from app.intelligence.eligibility import evaluate_eligibility
from app.intelligence.recommendation import compute_match_score, compute_readiness_score, apply_feedback_learning
from app.knowledge.hybrid_rag import HybridRAG
from app.schemas import MatchResult, OpportunityResponse, RecommendationResponse
from app.workflow.engine import WorkflowEngine, build_checklist


class ScholarshipAgent:
    """Thin orchestration layer over shared intelligence + workflow services."""

    def __init__(self) -> None:
        self.rag = HybridRAG()
        self.workflow = WorkflowEngine()

    def recommend(
        self,
        db: Session,
        profile: StudentProfile | None,
        query: str | None = None,
        state: str | None = None,
        limit: int = 20,
    ) -> RecommendationResponse:
        """
        Generate personalized scholarship recommendations with feedback-based learning.
        
        This method:
        1. Retrieves active scholarship opportunities
        2. Filters by state if specified
        3. Applies semantic search if query provided
        4. Computes match scores with eligibility evaluation
        5. Applies feedback learning to adjust recommendations (Requirement 21.6)
        6. Returns top N matches sorted by adjusted score
        
        Args:
            db: Database session for queries and feedback integration
            profile: User's student profile (None for anonymous users)
            query: Optional semantic search query
            state: Optional state filter
            limit: Maximum number of recommendations to return
        
        Returns:
            RecommendationResponse with matched opportunities and readiness score
        
        **Validates: Requirement 21.6** - Use negative feedback to improve future recommendations
        """
        opportunities = (
            db.query(Opportunity)
            .filter_by(category=OpportunityCategory.SCHOLARSHIP, is_active=True)
            .all()
        )

        if state:
            opportunities = [
                o
                for o in opportunities
                if not o.state_filter or "ALL" in o.state_filter or state in o.state_filter
            ]

        if query:
            semantic = self.rag.semantic_search(query, limit=limit, category="scholarship")
            id_order = {s["opportunity_id"]: s["score"] for s in semantic if s.get("opportunity_id")}
            opportunities = [o for o in opportunities if o.id in id_order]
            opportunities.sort(key=lambda o: id_order.get(o.id, 0), reverse=True)
        else:
            opportunities = opportunities[: limit * 2]

        matches: list[MatchResult] = []
        for opp in opportunities:
            # Compute base match score
            score, eligibility, reasons = compute_match_score(profile, opp)
            
            # Apply feedback learning to adjust score (Requirement 21.6)
            # This penalizes opportunities similar to those the user marked as not_relevant or ineligible
            if profile:
                adjusted_score = apply_feedback_learning(profile, opp, score / 100.0, db)
                final_score = adjusted_score * 100.0
            else:
                final_score = score
            
            matches.append(
                MatchResult(
                    opportunity=OpportunityResponse.model_validate(opp),
                    match_score=final_score,
                    eligibility=eligibility,
                    reasons=reasons,
                )
            )

        matches.sort(key=lambda m: m.match_score, reverse=True)
        readiness = compute_readiness_score(profile)
        if profile:
            profile.readiness_score = readiness
            db.add(profile)
            db.commit()

        return RecommendationResponse(
            matches=matches[:limit],
            total=len(matches),
            readiness_score=readiness,
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

        existing = (
            db.query(Application)
            .filter_by(user_id=user_id, opportunity_id=opportunity_id)
            .first()
        )
        if existing:
            if saved and not existing.saved:
                existing.saved = True
                db.commit()
            return existing

        score, eligibility, _ = compute_match_score(profile, opp)
        checklist = build_checklist(
            opp.documents_required or [],
            (profile.documents if profile else []) or [],
        )

        app = Application(
            user_id=user_id,
            opportunity_id=opportunity_id,
            state=ApplicationState.DISCOVERED,
            match_score=score,
            eligibility_result=eligibility,
            checklist=checklist,
            saved=saved,
            progress_pct=10,
        )
        db.add(app)
        db.commit()
        db.refresh(app)

        self.workflow.transition(
            db, app, ApplicationState.ELIGIBILITY_CHECK, "system", "system", "Started scholarship workflow"
        )
        return self.workflow.auto_advance_eligibility(db, app, eligibility)

    def get_checklist(self, db: Session, application_id: str) -> list[dict]:
        app = db.query(Application).filter_by(id=application_id).first()
        if not app:
            raise ValueError("Application not found")
        return app.checklist or []

    def scan_deadlines(self, db: Session) -> int:
        """Create deadline reminder notifications for saved/active applications."""
        threshold = date.today() + timedelta(days=14)
        count = 0
        apps = (
            db.query(Application)
            .join(Opportunity)
            .filter(
                Application.saved.is_(True) | Application.state.notin_([ApplicationState.COMPLETED, ApplicationState.REJECTED]),
                Opportunity.deadline.isnot(None),
                Opportunity.deadline <= threshold,
                Opportunity.deadline >= date.today(),
            )
            .all()
        )
        for app in apps:
            opp = app.opportunity
            days = (opp.deadline - date.today()).days
            existing = (
                db.query(Notification)
                .filter_by(user_id=app.user_id, title=f"Deadline: {opp.title[:100]}")
                .first()
            )
            if existing:
                continue
            notif = Notification(
                user_id=app.user_id,
                title=f"Deadline: {opp.title[:100]}",
                body=f"{opp.title} closes in {days} days. Complete your application checklist.",
                channel="in_app",
            )
            db.add(notif)
            count += 1
        db.commit()
        return count
