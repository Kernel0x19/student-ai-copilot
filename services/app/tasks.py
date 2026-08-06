"""Celery tasks for continuous monitoring — run: celery -A app.tasks worker -B -l info"""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()
celery_app = Celery("edupilot", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "ingest-scholarships-daily": {
        "task": "app.tasks.run_daily_ingestion",
        "schedule": crontab(hour=2, minute=0),
    },
    "poll-data-sources-daily": {
        "task": "app.tasks.poll_data_sources",
        "schedule": crontab(hour=2, minute=0),
    },
    "scan-deadlines-hourly": {
        "task": "app.tasks.scan_deadline_reminders",
        "schedule": crontab(minute=0),
    },
}


@celery_app.task
def poll_data_sources():
    """Poll all registered data connectors using ConnectorOrchestrator
    
    Requirement 4.1: Scheduled opportunity polling infrastructure
    """
    from app.db.session import SessionLocal
    from app.ingestion.connector_registry import ConnectorOrchestrator

    db = SessionLocal()
    try:
        orchestrator = ConnectorOrchestrator(db_session=db)
        return orchestrator.run_all()
    finally:
        db.close()


@celery_app.task
def run_daily_ingestion():
    from app.db.session import SessionLocal
    from app.ingestion.pipeline import run_ingestion
    from app.ingestion.hackathon_pipeline import run_hackathon_ingestion

    db = SessionLocal()
    try:
        stats = run_ingestion(db)
        hackathon_stats = run_hackathon_ingestion(db)
        stats["hackathons"] = hackathon_stats
        return stats
    finally:
        db.close()


@celery_app.task
def verify_document_task(user_id: str, document_type: str, image_bytes_hex: str, application_id: str = None):
    """Async document verification task
    
    Requirement 8.5: Document verification Celery task
    """
    import asyncio
    from app.db.session import SessionLocal
    from app.verification.engine import AutoVerificationEngine

    db = SessionLocal()
    try:
        image_bytes = bytes.fromhex(image_bytes_hex)
        engine = AutoVerificationEngine(db)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            engine.verify_document(user_id, document_type, image_bytes, application_id)
        )
    finally:
        db.close()


@celery_app.task
def scan_deadline_reminders():
    from app.agents.scholarship import ScholarshipAgent
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        return {"created": ScholarshipAgent().scan_deadlines(db)}
    finally:
        db.close()

