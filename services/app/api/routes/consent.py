from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas import ConsentResponse, ConsentUpdate
from app.security.consent import CONSENT_PURPOSES, get_user_consents, update_consent

router = APIRouter(prefix="/consent", tags=["consent"])


@router.get("/purposes")
def list_purposes():
    return {"purposes": CONSENT_PURPOSES}


@router.get("", response_model=list[ConsentResponse])
def get_consents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_user_consents(db, user.id)
    return [ConsentResponse.model_validate(r) for r in records]


@router.post("", response_model=ConsentResponse)
def set_consent(
    body: ConsentUpdate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    record = update_consent(db, user, body.purpose, body.granted, ip)
    return ConsentResponse.model_validate(record)
