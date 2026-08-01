"""Deadline Reminder System

This module scans upcoming deadlines for user applications and enqueues reminders
at 7-day and 2-day thresholds with duplicate reminder prevention tracking.

Satisfies Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import Application, Opportunity, User, AuditLog
from app.notifications.service import NotificationType
from app.notifications.orchestrator import NotificationOrchestrator

logger = logging.getLogger(__name__)


class DeadlineMonitor:
    """Scans applications for upcoming opportunity deadlines and dispatches reminders.
    
    **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7**
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.orchestrator = NotificationOrchestrator(db_session)

    async def scan_and_notify_deadlines(self) -> Dict[str, Any]:
        """Scan applications for upcoming 7-day and 2-day deadlines and send notifications."""
        now = datetime.utcnow()
        day_7_target = now + timedelta(days=7)
        day_2_target = now + timedelta(days=2)
        
        # Query saved/in-progress applications with active opportunities
        applications = self.db.query(Application).filter(
            Application.saved == True,
            Application.state.in_(["discovered", "in_progress"])
        ).all()
        
        reminders_sent = 0
        reminders_skipped = 0
        
        for app in applications:
            opp = self.db.query(Opportunity).filter_by(id=app.opportunity_id).first()
            if not opp or not opp.deadline:
                continue
                
            deadline = opp.deadline
            days_remaining = (deadline - now).days
            
            # Check 7-day or 2-day thresholds
            is_7_day = 6 <= days_remaining <= 7
            is_2_day = 1 <= days_remaining <= 2
            
            if not (is_7_day or is_2_day):
                continue
                
            reminder_type = "7_day_reminder" if is_7_day else "2_day_reminder"
            
            # Prevent duplicate reminders via AuditLog deduplication check
            already_notified = self.db.query(AuditLog).filter(
                AuditLog.action == "deadline_reminder_sent",
                AuditLog.resource_type == "application",
                AuditLog.resource_id == str(app.id),
                AuditLog.details.like(f"%{reminder_type}%")
            ).first()
            
            if already_notified:
                reminders_skipped += 1
                continue
                
            title = f"Deadline Reminder: {opp.title}"
            body = f"The deadline for '{opp.title}' is in {days_remaining} days ({deadline.strftime('%Y-%m-%d')}). Don't miss out!"
            
            await self.orchestrator.send_notification(
                user_id=app.user_id,
                notification_type=NotificationType.DEADLINE_REMINDER,
                title=title,
                body=body,
                metadata={"opportunity_id": opp.id, "application_id": app.id, "days_remaining": days_remaining}
            )
            
            # Record audit entry for deduplication tracking
            audit_entry = AuditLog(
                action="deadline_reminder_sent",
                resource_type="application",
                resource_id=str(app.id),
                details={"reminder_type": reminder_type, "days_remaining": days_remaining},
                created_at=datetime.utcnow()
            )
            self.db.add(audit_entry)
            reminders_sent += 1

        self.db.commit()
        return {
            "reminders_sent": reminders_sent,
            "reminders_skipped_duplicate": reminders_skipped,
            "scanned_at": now.isoformat()
        }
