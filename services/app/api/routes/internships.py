from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.internship import InternshipAgent
from app.api.deps import get_current_user, get_student_profile
from app.db.models import Application, Opportunity, OpportunityCategory, StudentProfile, User
from app.db.session import get_db
from app.schemas import (
    ApplicationCreate, ApplicationResponse,
    OpportunityResponse, RecommendationResponse, SearchRequest,
)

router = APIRouter(prefix="/internships", tags=["internships"])
agent  = InternshipAgent()


@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    query:        str | None = None,
    state:        str | None = None,
    location:     str | None = None,
    work_type:    str | None = None,
    duration_max: int | None = None,
    stipend_min:  int | None = None,
    source:       str | None = None,
    limit:        int = 30,
    user:         User         = Depends(get_current_user),
    profile:      StudentProfile | None = Depends(get_student_profile),
    db:           Session      = Depends(get_db),
):
    return agent.recommend(
        db, profile,
        query=query, state=state, location=location,
        work_type=work_type, duration_max=duration_max,
        stipend_min=stipend_min, source=source, limit=limit,
    )


@router.post("/search", response_model=RecommendationResponse)
def search_internships(
    body:    SearchRequest,
    user:    User         = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db:      Session      = Depends(get_db),
):
    return agent.recommend(db, profile, query=body.query, state=body.state, limit=body.limit)


@router.get("/opportunities", response_model=list[OpportunityResponse])
def list_opportunities(db: Session = Depends(get_db)):
    opps = db.query(Opportunity).filter_by(
        category=OpportunityCategory.INTERNSHIP, is_active=True
    ).all()
    return [OpportunityResponse.model_validate(o) for o in opps]


@router.post("/applications", response_model=ApplicationResponse)
def create_application(
    body:    ApplicationCreate,
    user:    User         = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db:      Session      = Depends(get_db),
):
    try:
        app = agent.start_application(db, user.id, body.opportunity_id, profile, saved=body.saved)
    except ValueError as e:
        raise HTTPException(404, str(e))
    resp = ApplicationResponse.model_validate(app)
    resp.opportunity = OpportunityResponse.model_validate(app.opportunity) if app.opportunity else None
    return resp


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    apps = (
        db.query(Application)
        .filter_by(user_id=user.id)
        .join(Opportunity)
        .filter(Opportunity.category == OpportunityCategory.INTERNSHIP)
        .order_by(Application.updated_at.desc())
        .all()
    )
    result = []
    for app in apps:
        resp = ApplicationResponse.model_validate(app)
        if app.opportunity:
            resp.opportunity = OpportunityResponse.model_validate(app.opportunity)
        result.append(resp)
    return result
