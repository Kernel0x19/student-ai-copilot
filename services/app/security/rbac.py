from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User, UserRole
from app.db.session import get_db


def require_role(*roles: UserRole):
    def checker(user: User = Depends(lambda: None)):
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        if user.role not in roles and UserRole.ADMIN not in roles:
            if user.role not in roles:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return checker


def can_review(user: User) -> bool:
    return user.role in (UserRole.REVIEWER, UserRole.ADMIN)


def can_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


def ensure_user(db: Session, user_id: str, email: str = "") -> User:
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id, email=email or f"{user_id}@local.dev")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
