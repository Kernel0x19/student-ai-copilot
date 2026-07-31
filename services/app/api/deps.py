from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import StudentProfile, User
from app.db.session import get_db
from app.security.rbac import ensure_user

settings = get_settings()


async def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
) -> User:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        if settings.supabase_jwt_secret:
            try:
                payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
                user_id = payload.get("sub")
                email = payload.get("email", "")
                if user_id:
                    return ensure_user(db, user_id, email)
            except JWTError:
                pass

    if settings.dev_mode and x_user_id:
        return ensure_user(db, x_user_id, x_user_email or "")

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")


async def get_student_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentProfile | None:
    return db.query(StudentProfile).filter_by(user_id=user.id).first()
