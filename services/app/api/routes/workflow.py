from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Application, Notification, User, UserRole
from app.db.session import get_db
from app.schemas import NotificationResponse, WorkflowTransitionRequest
from app.schemas import ApplicationResponse, ApplicationState
from app.schemas import OpportunityResponse
from app.security.rbac import can_review
from app.workflow.engine import WorkflowEngine

router = APIRouter(prefix="/workflow", tags=["workflow"])
engine = WorkflowEngine()


@router.post("/applications/{application_id}/transition", response_model=ApplicationResponse)
def transition_application(
    application_id: str,
    body: WorkflowTransitionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = db.query(Application).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    if app.user_id != user.id and not can_review(user):
        raise HTTPException(403, "Not authorized")

    if body.to_state in (ApplicationState.HUMAN_REVIEW, ApplicationState.COMPLETED) and not can_review(user):
        if body.to_state != ApplicationState.SUBMITTED:
            raise HTTPException(403, "Reviewer role required")

    try:
        app = engine.transition(db, app, body.to_state, user.id, user.role.value, body.notes)
    except ValueError as e:
        raise HTTPException(400, str(e))

    resp = ApplicationResponse.model_validate(app)
    if app.opportunity:
        resp.opportunity = OpportunityResponse.model_validate(app.opportunity)
    return resp


@router.get("/applications/{application_id}/history")
def workflow_history(
    application_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.db.models import WorkflowEvent

    app = db.query(Application).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    if app.user_id != user.id and not can_review(user):
        raise HTTPException(403, "Not authorized")

    events = (
        db.query(WorkflowEvent)
        .filter_by(application_id=application_id)
        .order_by(WorkflowEvent.created_at)
        .all()
    )
    return [
        {
            "from_state": e.from_state,
            "to_state": e.to_state,
            "actor_role": e.actor_role,
            "notes": e.notes,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
