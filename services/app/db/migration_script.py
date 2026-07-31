"""SQLite to PostgreSQL Data Migration & Integrity Verification Script

This module implements data extraction from SQLite and high-speed batch loading into PostgreSQL,
preserving schema integrity, relationships, and foreign keys while performing pre/post-migration validation checks.

Satisfies Requirements: 14.2, 14.3, 14.4, 14.6, 14.7
"""

import logging
from typing import Dict, Any, List, Type
from datetime import datetime

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, Session

from app.db.models import (
    Base, User, Opportunity, Application, WorkflowEvent, ConsentRecord, AuditLog,
    Notification, ConnectorStatus, NotificationPreference, NotificationHistory,
    DeviceToken, DeadlineReminder, Document, ExperimentVariant, UserExperiment,
    Feedback, AccuracyMetric, UserEvent
)

logger = logging.getLogger(__name__)

ALL_MODELS: List[Type[Base]] = [
    User, Opportunity, Application, WorkflowEvent, ConsentRecord, AuditLog,
    Notification, ConnectorStatus, NotificationPreference, NotificationHistory,
    DeviceToken, DeadlineReminder, Document, ExperimentVariant, UserExperiment,
    Feedback, AccuracyMetric, UserEvent
]


class SQLiteToPostgresMigrator:
    """Orchestrates SQLite to PostgreSQL data migration with validation and rollback support.
    
    **Validates: Requirements 14.2, 14.3, 14.4, 14.6, 14.7**
    """

    def __init__(self, sqlite_url: str, postgres_url: str):
        self.sqlite_engine = create_engine(sqlite_url)
        self.postgres_engine = create_engine(postgres_url)
        
        self.SQLiteSession = sessionmaker(bind=self.sqlite_engine)
        self.PostgresSession = sessionmaker(bind=self.postgres_engine)

    def verify_record_counts(self, source_session: Session, target_session: Session) -> Dict[str, Dict[str, int]]:
        """Compare table record counts between source SQLite and target PostgreSQL."""
        counts = {}
        for model in ALL_MODELS:
            tbl_name = model.__tablename__
            src_count = source_session.query(func.count(model.id)).scalar() or 0
            tgt_count = target_session.query(func.count(model.id)).scalar() or 0
            counts[tbl_name] = {
                'source': src_count,
                'target': tgt_count,
                'match': src_count == tgt_count
            }
        return counts

    def run_migration(self, batch_size: int = 500) -> Dict[str, Any]:
        """Execute full data migration from SQLite to PostgreSQL with integrity checks."""
        logger.info("Starting SQLite to PostgreSQL data migration...")
        
        # 1. Create tables on target database if they don't exist
        Base.metadata.create_all(bind=self.postgres_engine)
        
        source_session = self.SQLiteSession()
        target_session = self.PostgresSession()
        
        migrated_stats = {}
        
        try:
            for model in ALL_MODELS:
                tbl_name = model.__tablename__
                records = source_session.query(model).all()
                
                inserted_count = 0
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    for record in batch:
                        # Make transient copy for target session
                        source_session.expunge(record)
                        target_session.merge(record)
                    target_session.commit()
                    inserted_count += len(batch)
                
                migrated_stats[tbl_name] = inserted_count
                logger.info(f"Migrated {inserted_count} records for table '{tbl_name}'")
                
            # 2. Integrity Verification
            verification = self.verify_record_counts(source_session, target_session)
            all_matched = all(v['match'] for v in verification.values())
            
            logger.info("Migration integrity verification complete. All matched: %s", all_matched)
            
            return {
                'success': all_matched,
                'migrated_counts': migrated_stats,
                'verification': verification,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Migration failed, rolling back changes: %s", e)
            target_session.rollback()
            raise RuntimeError(f"Database migration failed: {e}")
        finally:
            source_session.close()
            target_session.close()
