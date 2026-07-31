from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.scholarship import ScholarshipAgent
from app.api.deps import get_current_user, get_student_profile
from app.db.models import Application, Notification, OpportunityCategory, StudentProfile, User
from app.db.session import get_db
from app.intelligence.recommendation import compute_readiness_score
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    DashboardStats,
    MatchResult,
    OpportunityResponse,
    RecommendationResponse,
    SearchRequest,
)
from app.schemas import OpportunityCategory as OppCat

router = APIRouter(prefix="/scholarships", tags=["scholarships"])
agent = ScholarshipAgent()


@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    query: str | None = None,
    state: str | None = None,
    limit: int = 20,
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    return agent.recommend(db, profile, query=query, state=state, limit=limit)


@router.post("/search", response_model=RecommendationResponse)
def search_scholarships(
    body: SearchRequest,
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    return agent.recommend(db, profile, query=body.query, state=body.state, limit=body.limit)


@router.get("/opportunities", response_model=list[OpportunityResponse])
def list_opportunities(db: Session = Depends(get_db)):
    from app.db.models import Opportunity

    opps = db.query(Opportunity).filter_by(category=OpportunityCategory.SCHOLARSHIP, is_active=True).all()
    return [OpportunityResponse.model_validate(o) for o in opps]


@router.post("/applications", response_model=ApplicationResponse)
def create_application(
    body: ApplicationCreate,
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    try:
        app = agent.start_application(db, user.id, body.opportunity_id, profile, saved=body.saved)
    except ValueError as e:
        raise HTTPException(404, str(e))
    opp = app.opportunity
    resp = ApplicationResponse.model_validate(app)
    resp.opportunity = OpportunityResponse.model_validate(opp) if opp else None
    return resp


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    apps = db.query(Application).filter_by(user_id=user.id).order_by(Application.updated_at.desc()).all()
    result = []
    for app in apps:
        resp = ApplicationResponse.model_validate(app)
        if app.opportunity:
            resp.opportunity = OpportunityResponse.model_validate(app.opportunity)
        result.append(resp)
    return result


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    from app.db.models import Opportunity

    rec = agent.recommend(db, profile, limit=100)
    internships = db.query(Opportunity).filter_by(category=OppCat.INTERNSHIP, is_active=True).count()
    apps = db.query(Application).filter_by(user_id=user.id).count()
    docs = len(profile.documents) if profile and profile.documents else 0
    return DashboardStats(
        scholarships_matched=len([m for m in rec.matches if m.match_score >= 40]),
        internships_available=internships,
        documents_uploaded=docs,
        applications_tracked=apps,
        readiness_score=compute_readiness_score(profile),
    )
