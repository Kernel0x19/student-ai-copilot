from datetime import datetime

from app.db.models import Application, ApplicationState, WorkflowEvent
from app.security.rbac import can_review

TRANSITIONS: dict[ApplicationState, list[ApplicationState]] = {
    ApplicationState.DISCOVERED: [ApplicationState.ELIGIBILITY_CHECK],
    ApplicationState.ELIGIBILITY_CHECK: [
        ApplicationState.DOCUMENT_VALIDATION,
        ApplicationState.REJECTED,
    ],
    ApplicationState.DOCUMENT_VALIDATION: [
        ApplicationState.HUMAN_REVIEW,
        ApplicationState.REJECTED,
    ],
    ApplicationState.HUMAN_REVIEW: [
        ApplicationState.SUBMITTED,
        ApplicationState.REJECTED,
    ],
    ApplicationState.SUBMITTED: [ApplicationState.TRACKING],
    ApplicationState.TRACKING: [ApplicationState.COMPLETED, ApplicationState.REJECTED],
    ApplicationState.COMPLETED: [],
    ApplicationState.REJECTED: [],
}

STATE_PROGRESS = {
    ApplicationState.DISCOVERED: 10,
    ApplicationState.ELIGIBILITY_CHECK: 25,
    ApplicationState.DOCUMENT_VALIDATION: 45,
    ApplicationState.HUMAN_REVIEW: 60,
    ApplicationState.SUBMITTED: 80,
    ApplicationState.TRACKING: 90,
    ApplicationState.COMPLETED: 100,
    ApplicationState.REJECTED: 0,
}


def build_checklist(documents_required: list[str], uploaded: list[dict]) -> list[dict]:
    uploaded_types = {d.get("type") for d in uploaded}
    return [
        {
            "document": doc,
            "status": "uploaded" if doc in uploaded_types else "pending",
            "required": True,
        }
        for doc in documents_required
    ]


class WorkflowEngine:
    def transition(
        self,
        db,
        application: Application,
        to_state: ApplicationState,
        actor_id: str,
        actor_role: str,
        notes: str | None = None,
    ) -> Application:
        allowed = TRANSITIONS.get(application.state, [])
        if to_state not in allowed:
            raise ValueError(f"Cannot transition from {application.state.value} to {to_state.value}")

        if to_state == ApplicationState.HUMAN_REVIEW and actor_role == "student":
            raise ValueError("Human review requires reviewer approval")

        event = WorkflowEvent(
            application_id=application.id,
            from_state=application.state.value,
            to_state=to_state.value,
            actor_id=actor_id,
            actor_role=actor_role,
            notes=notes,
        )
        db.add(event)

        application.state = to_state
        application.progress_pct = STATE_PROGRESS.get(to_state, application.progress_pct)
        application.updated_at = datetime.utcnow()
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    def auto_advance_eligibility(self, db, application: Application, eligibility: dict) -> Application:
        application.eligibility_result = eligibility
        if eligibility.get("eligible"):
            return self.transition(
                db,
                application,
                ApplicationState.DOCUMENT_VALIDATION,
                actor_id="system",
                actor_role="system",
                notes="Auto-advanced after eligibility pass",
            )
        return self.transition(
            db,
            application,
            ApplicationState.REJECTED,
            actor_id="system",
            actor_role="system",
            notes="Failed eligibility check",
        )
