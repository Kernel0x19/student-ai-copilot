import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    STUDENT = "student"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class OpportunityCategory(str, enum.Enum):
    SCHOLARSHIP = "scholarship"
    INTERNSHIP = "internship"
    PLACEMENT = "placement"
    HACKATHON = "hackathon"


class ApplicationState(str, enum.Enum):
    DISCOVERED = "discovered"
    ELIGIBILITY_CHECK = "eligibility_check"
    DOCUMENT_VALIDATION = "document_validation"
    HUMAN_REVIEW = "human_review"
    SUBMITTED = "submitted"
    TRACKING = "tracking"
    COMPLETED = "completed"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), index=True)  # For SMS notifications
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped["StudentProfile | None"] = relationship(back_populates="user", uselist=False)
    consents: Mapped[list["ConsentRecord"]] = relationship(back_populates="user")
    applications: Mapped[list["Application"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(32))
    phone: Mapped[str | None] = mapped_column(String(20))
    state: Mapped[str | None] = mapped_column(String(64))
    district: Mapped[str | None] = mapped_column(String(64))
    category: Mapped[str | None] = mapped_column(String(32))  # SC/ST/OBC/General/EWS
    income_annual: Mapped[float | None] = mapped_column(Float)
    aadhaar_last4: Mapped[str | None] = mapped_column(String(4))
    college: Mapped[str | None] = mapped_column(String(255))
    university: Mapped[str | None] = mapped_column(String(255))
    stream: Mapped[str | None] = mapped_column(String(128))
    degree: Mapped[str | None] = mapped_column(String(128))
    year_of_study: Mapped[int | None] = mapped_column(Integer)
    cgpa: Mapped[float | None] = mapped_column(Float)
    percentage_12th: Mapped[float | None] = mapped_column(Float)
    skills: Mapped[list | None] = mapped_column(JSON, default=list)
    documents: Mapped[list | None] = mapped_column(JSON, default=list)
    preferences: Mapped[dict | None] = mapped_column(JSON, default=dict)
    backlogs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="profile")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    external_id: Mapped[str | None] = mapped_column(String(128), index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), unique=True, index=True)  # For deduplication
    category: Mapped[OpportunityCategory] = mapped_column(Enum(OpportunityCategory), index=True)
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text)
    amount_min: Mapped[float | None] = mapped_column(Float)
    amount_max: Mapped[float | None] = mapped_column(Float)
    deadline: Mapped[date | None] = mapped_column(Date, index=True)
    eligibility_rules: Mapped[dict | None] = mapped_column(JSON, default=dict)
    documents_required: Mapped[list | None] = mapped_column(JSON, default=list)
    application_url: Mapped[str | None] = mapped_column(String(1024))
    state_filter: Mapped[list | None] = mapped_column(JSON, default=list)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    raw_data: Mapped[dict | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    embedding_id: Mapped[str | None] = mapped_column(String(128))
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_source_external"),)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id"), index=True)
    state: Mapped[ApplicationState] = mapped_column(Enum(ApplicationState), default=ApplicationState.DISCOVERED)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    eligibility_result: Mapped[dict | None] = mapped_column(JSON)
    checklist: Mapped[list | None] = mapped_column(JSON, default=list)
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0)
    saved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="applications")
    opportunity: Mapped["Opportunity"] = relationship()
    workflow_events: Mapped[list["WorkflowEvent"]] = relationship(back_populates="application")


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"), index=True)
    from_state: Mapped[str | None] = mapped_column(String(64))
    to_state: Mapped[str] = mapped_column(String(64))
    actor_id: Mapped[str | None] = mapped_column(String(36))
    actor_role: Mapped[str | None] = mapped_column(String(32))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["Application"] = relationship(back_populates="workflow_events")


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    purpose: Mapped[str] = mapped_column(String(128))
    granted: Mapped[bool] = mapped_column(Boolean, default=False)
    granted_at: Mapped[datetime | None] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    ip_address: Mapped[str | None] = mapped_column(String(64))

    user: Mapped["User"] = relationship(back_populates="consents")

    __table_args__ = (UniqueConstraint("user_id", "purpose", name="uq_user_consent_purpose"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(128), index=True)
    resource_type: Mapped[str] = mapped_column(String(64), index=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), index=True)
    details: Mapped[dict | None] = mapped_column(JSON)
    audit_metadata: Mapped[dict | None] = mapped_column(JSON)  # Additional context like old/new values
    ip_address: Mapped[str | None] = mapped_column(String(64))
    consent_id: Mapped[str | None] = mapped_column(String(36))  # Reference to consent for sensitive operations
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user: Mapped["User | None"] = relationship(back_populates="audit_logs")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String(32), default="in_app")
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications")


class ConnectorStatus(Base):
    """Track data connector execution status and freshness"""

    __tablename__ = "connector_status"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    last_run: Mapped[datetime | None] = mapped_column(DateTime)
    last_success: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    last_error: Mapped[str | None] = mapped_column(Text)
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationPreference(Base):
    """User notification channel preferences"""

    __tablename__ = "notification_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, index=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    deadline_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    new_matches: Mapped[bool] = mapped_column(Boolean, default=True)
    status_updates: Mapped[bool] = mapped_column(Boolean, default=True)
    deadline_changes: Mapped[bool] = mapped_column(Boolean, default=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationHistory(Base):
    """Log of all sent notifications for tracking delivery"""

    __tablename__ = "notification_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    notification_type: Mapped[str] = mapped_column(String(64), index=True)
    channel: Mapped[str] = mapped_column(String(32), index=True)
    recipient: Mapped[str] = mapped_column(String(255))
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str | None] = mapped_column(Text)
    message_id: Mapped[str | None] = mapped_column(String(128))
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class DeviceToken(Base):
    """Firebase device tokens for push notifications"""

    __tablename__ = "device_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(512), unique=True)
    platform: Mapped[str] = mapped_column(String(32))  # ios, android, web
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeadlineReminder(Base):
    """Track sent deadline reminders to prevent duplicates"""

    __tablename__ = "deadline_reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id"), index=True)
    reminder_type: Mapped[str] = mapped_column(String(32))  # 7_day, 2_day
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "opportunity_id", "reminder_type", name="uq_user_opp_reminder"),)


class Document(Base):
    """Encrypted document storage with verification tracking"""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(64), index=True)  # aadhaar, income_certificate, etc.
    file_path: Mapped[str] = mapped_column(String(512))  # Encrypted file location
    encryption_key_id: Mapped[str] = mapped_column(String(128))  # Reference to key in KMS
    verification_status: Mapped[str] = mapped_column(
        String(32), default="pending"
    )  # pending, processing, auto_approved, needs_review, rejected
    extracted_fields: Mapped[dict | None] = mapped_column(JSON)
    field_confidences: Mapped[dict | None] = mapped_column(JSON)
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    gov_verification_status: Mapped[str | None] = mapped_column(
        String(32)
    )  # verified, failed, api_unavailable, not_applicable
    gov_verification_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExperimentVariant(Base):
    """A/B testing experiment definitions"""

    __tablename__ = "experiment_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    experiment_name: Mapped[str] = mapped_column(String(128), index=True)
    variant_name: Mapped[str] = mapped_column(String(64))  # control, treatment_a, treatment_b
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict | None] = mapped_column(JSON)  # Variant-specific configuration
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("experiment_name", "variant_name", name="uq_experiment_variant"),)


class UserExperiment(Base):
    """Track user assignment to experiment variants"""

    __tablename__ = "user_experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    experiment_name: Mapped[str] = mapped_column(String(128), index=True)
    variant_name: Mapped[str] = mapped_column(String(64))
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "experiment_name", name="uq_user_experiment"),)


class Feedback(Base):
    """User feedback on recommendations and opportunities"""

    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id"), index=True)
    feedback_type: Mapped[str] = mapped_column(
        String(32), index=True
    )  # relevant, not_relevant, ineligible, applied, ignored
    comment: Mapped[str | None] = mapped_column(Text)
    experiment_name: Mapped[str | None] = mapped_column(String(128))
    variant_name: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class AccuracyMetric(Base):
    """Track false positives and false negatives in eligibility checking"""

    __tablename__ = "accuracy_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id"), index=True)
    metric_type: Mapped[str] = mapped_column(String(32), index=True)  # false_positive, false_negative
    predicted_eligible: Mapped[bool] = mapped_column(Boolean)
    actual_eligible: Mapped[bool] = mapped_column(Boolean)
    rule_context: Mapped[dict | None] = mapped_column(JSON)  # Which rules failed/passed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class UserEvent(Base):
    """
    Analytics event tracking for user actions and interactions.
    
    This table captures detailed user interaction events for analytics,
    A/B testing analysis, and recommendation improvement.
    
    **Validates: Requirements 20.1, 20.2, 20.3, 21.1, 21.2**
    """

    __tablename__ = "user_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)  # recommendation_viewed, saved, applied, dismissed, profile_updated, etc.
    opportunity_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("opportunities.id"), index=True)
    application_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("applications.id"))
    experiment_name: Mapped[str | None] = mapped_column(String(128), index=True)
    variant_name: Mapped[str | None] = mapped_column(String(64), index=True)
    match_score: Mapped[float | None] = mapped_column(Float)
    event_metadata: Mapped[dict | None] = mapped_column(JSON)  # Additional event-specific data
    session_id: Mapped[str | None] = mapped_column(String(128), index=True)  # For session-based analytics
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        # Index for common query patterns
        # Composite index for experiment analysis queries
        # CREATE INDEX idx_user_events_experiment ON user_events(experiment_name, variant_name, event_type, created_at)
    )


class ChatThread(Base):
    """A persistent, user-owned conversation thread."""

    __tablename__ = "chat_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), default="New conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessageRecord(Base):
    """A durable message record; LangGraph uses the latest records as short-term context."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    thread_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_threads.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class UserMemory(Base):
    """Long-term, user-approved-or-inferred facts used to personalize future chats."""

    __tablename__ = "user_memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(32), default="chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
