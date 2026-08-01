from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_student_profile
from app.db.models import StudentProfile, User
from app.db.session import get_db
from app.intelligence.recommendation import compute_readiness_score
from app.schemas import StudentProfileCreate, StudentProfileResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=StudentProfileResponse | None)
def get_profile(profile: StudentProfile | None = Depends(get_student_profile)):
    if not profile:
        return None
    return StudentProfileResponse.model_validate(profile)


@router.put("", response_model=StudentProfileResponse)
def upsert_profile(
    body: StudentProfileCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not profile:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    profile.readiness_score = compute_readiness_score(profile)
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return StudentProfileResponse.model_validate(profile)
