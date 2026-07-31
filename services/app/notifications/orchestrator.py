"""Notification Orchestrator

This module provides multi-channel notification coordination based on user preferences.
It checks user notification preferences, selects appropriate channels (Email, SMS, Push, In-App),
and logs delivery history.

Satisfies Requirements: 10.2, 10.6, 11.2, 12.2
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import NotificationPreference, NotificationHistory, User
from app.notifications.service import NotificationChannel, NotificationType
from app.notifications.email import EmailNotificationService
from app.notifications.sms import SMSNotificationService
from app.notifications.push import PushNotificationService

logger = logging.getLogger(__name__)


class NotificationOrchestrator:
    """Orchestrates notification dispatch across user-preferred channels.
    
    **Validates: Requirements 10.2, 10.6, 11.2, 12.2**
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.email_service = EmailNotificationService()
        self.sms_service = SMSNotificationService()
        self.push_service = PushNotificationService()

    def get_user_channels(self, user_id: str, notification_type: NotificationType) -> List[NotificationChannel]:
        """Determine enabled channels for user and notification type."""
        pref = self.db.query(NotificationPreference).filter_by(user_id=user_id).first()
        
        if not pref:
            # Default preferences: Email and In-App enabled
            return [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            
        enabled = [NotificationChannel.IN_APP]
        
        if pref.email_enabled:
            enabled.append(NotificationChannel.EMAIL)
        if pref.sms_enabled:
            enabled.append(NotificationChannel.SMS)
        if pref.push_enabled:
            enabled.append(NotificationChannel.PUSH)
            
        return enabled

    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        body: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send multi-channel notification to a user based on preferences.
        
        Args:
            user_id: Target user ID
            notification_type: Enum indicating notification type
            title: Notification title / subject
            body: Notification body text
            metadata: Optional additional data (e.g. opportunity_id)
        """
        user = self.db.query(User).filter_by(id=user_id).first()
        channels = self.get_user_channels(user_id, notification_type)
        results = {}
        
        for channel in channels:
            delivery_status = "sent"
            error_msg = None
            
            if channel == NotificationChannel.EMAIL and user and user.email:
                res = await self.email_service.send(
                    user.email,
                    {'subject': title, 'body': body}
                )
                results['email'] = res
                if not res.get('success'):
                    delivery_status = "failed"
                    error_msg = res.get('error')
                    
            elif channel == NotificationChannel.SMS and hasattr(user, 'phone_number') and user.phone_number:
                res = await self.sms_service.send(
                    user.phone_number,
                    {'body': body}
                )
                results['sms'] = res
                if not res.get('success'):
                    delivery_status = "failed"
                    error_msg = res.get('error')
                    
            elif channel == NotificationChannel.PUSH and hasattr(user, 'device_token') and user.device_token:
                res = await self.push_service.send(
                    user.device_token,
                    {'title': title, 'body': body, 'data': metadata or {}}
                )
                results['push'] = res
                if not res.get('success'):
                    delivery_status = "failed"
                    error_msg = res.get('error')

            # Log to notification history database table
            recipient_id = ""
            was_success = delivery_status == "sent"
            if channel == NotificationChannel.EMAIL and user:
                recipient_id = user.email or ""
            elif channel == NotificationChannel.SMS and user and hasattr(user, 'phone_number'):
                recipient_id = user.phone_number or ""
            elif channel == NotificationChannel.PUSH and user and hasattr(user, 'device_token'):
                recipient_id = user.device_token or ""
            
            history_entry = NotificationHistory(
                user_id=user_id,
                notification_type=notification_type.value,
                channel=channel.value,
                recipient=recipient_id,
                success=was_success,
                error=error_msg,
                sent_at=datetime.utcnow()
            )
            self.db.add(history_entry)
            
        self.db.commit()
        return {
            'user_id': user_id,
            'notification_type': notification_type.value,
            'channels_attempted': [c.value for c in channels],
            'channel_results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
