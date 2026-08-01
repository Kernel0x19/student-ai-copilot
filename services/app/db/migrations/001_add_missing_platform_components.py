"""
Migration 001: Add Missing Platform Components Tables

This migration adds all new tables required for:
- Data connector tracking
- Multi-channel notifications
- Document verification
- A/B testing
- Feedback and accuracy tracking

Run with: python -m app.db.migrations.001_add_missing_platform_components
"""

from sqlalchemy import text

from app.db.session import SessionLocal, engine


def upgrade():
    """Apply migration"""
    print("Running migration 001: Add Missing Platform Components")

    with SessionLocal() as db:
        # Add phone_number to users table
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)"))
            print("✓ Added phone_number to users table")
        except Exception as e:
            print(f"⚠ Could not add phone_number (may already exist): {e}")

        # Add source_url to opportunities table
        try:
            db.execute(text("ALTER TABLE opportunities ADD COLUMN source_url VARCHAR(1024)"))
            print("✓ Added source_url to opportunities table")
        except Exception as e:
            print(f"⚠ Could not add source_url (may already exist): {e}")

        # Add metadata, ip_address, consent_id to audit_logs
        try:
            db.execute(text("ALTER TABLE audit_logs ADD COLUMN metadata JSON"))
            db.execute(text("ALTER TABLE audit_logs ADD COLUMN ip_address VARCHAR(64)"))
            db.execute(text("ALTER TABLE audit_logs ADD COLUMN consent_id VARCHAR(36)"))
            print("✓ Added metadata, ip_address, consent_id to audit_logs table")
        except Exception as e:
            print(f"⚠ Could not add audit_logs columns (may already exist): {e}")

        db.commit()

    # Create all new tables using SQLAlchemy
    from app.db.models import (
        AccuracyMetric,
        ConnectorStatus,
        DeadlineReminder,
        DeviceToken,
        Document,
        ExperimentVariant,
        Feedback,
        NotificationHistory,
        NotificationPreference,
        UserExperiment,
    )
    from app.db.session import Base

    Base.metadata.create_all(bind=engine)
    print("✓ Created all new tables")

    print("Migration 001 completed successfully!")


def downgrade():
    """Revert migration (not implemented for safety)"""
    print("Downgrade not implemented. Create a backup before applying migrations.")
    raise NotImplementedError("Downgrade not supported")


if __name__ == "__main__":
    upgrade()
