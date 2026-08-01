from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import AuditLog, ConsentRecord, User


CONSENT_PURPOSES = [
    "aadhaar_verification",
    "income_certificate_processing",
    "eligibility_auto_check",
    "document_ocr",
    "notification_email",
    "notification_sms",
]


def get_user_consents(db: Session, user_id: str) -> list[ConsentRecord]:
    return db.query(ConsentRecord).filter_by(user_id=user_id).all()


def update_consent(
    db: Session,
    user: User,
    purpose: str,
    granted: bool,
    ip_address: str | None = None,
) -> ConsentRecord:
    if purpose not in CONSENT_PURPOSES:
        raise ValueError(f"Unknown consent purpose: {purpose}")

    record = db.query(ConsentRecord).filter_by(user_id=user.id, purpose=purpose).first()
    if not record:
        record = ConsentRecord(user_id=user.id, purpose=purpose)
        db.add(record)

    record.granted = granted
    if granted:
        record.granted_at = datetime.utcnow()
        record.revoked_at = None
    else:
        record.revoked_at = datetime.utcnow()

    record.ip_address = ip_address
    db.add(record)

    log_audit(db, user.id, "consent_updated", "consent", record.id, {"purpose": purpose, "granted": granted})
    db.commit()
    db.refresh(record)
    return record


def has_consent(db: Session, user_id: str, purpose: str) -> bool:
    record = db.query(ConsentRecord).filter_by(user_id=user_id, purpose=purpose, granted=True).first()
    return record is not None


def log_audit(
    db: Session,
    user_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )
    db.add(entry)
    return entry
