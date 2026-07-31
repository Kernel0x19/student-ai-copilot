"""
Notification Service Abstractions

This module provides the base abstractions for multi-channel notification delivery.
It defines the core interfaces that concrete notification service implementations
(email, SMS, push) must implement.

**Validates: Requirements 10.1, 11.1, 12.1**
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NotificationType(Enum):
    """Types of notifications that can be sent to users"""

    DEADLINE_REMINDER = "deadline_reminder"
    APPLICATION_STATUS = "application_status_change"
    NEW_MATCH = "new_match"
    DEADLINE_CHANGE = "deadline_change"


class NotificationChannel(Enum):
    """Communication channels for notification delivery"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationService(ABC):
    """
    Abstract base class for all notification delivery services.

    This interface defines the contract that all notification service implementations
    (EmailNotificationService, SMSNotificationService, PushNotificationService)
    must follow.

    Concrete implementations are responsible for:
    - Integrating with third-party services (SendGrid, Twilio, FCM)
    - Handling retries and error recovery
    - Logging delivery status
    """

    @abstractmethod
    async def send(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a notification to the specified recipient.

        Args:
            recipient: The recipient identifier (email address, phone number, or device token)
            message: Dictionary containing message content. Structure varies by channel:
                - Email: {'subject': str, 'body': str, 'html': str (optional)}
                - SMS: {'body': str}
                - Push: {'title': str, 'body': str, 'data': dict (optional)}

        Returns:
            Dictionary with delivery status:
            {
                'success': bool,
                'message_id': str (optional),
                'error': str (optional),
                'status_code': int (optional)
            }

        Raises:
            NotImplementedError: Must be implemented by concrete service classes
        """
        pass

    @abstractmethod
    async def validate_recipient(self, recipient: str) -> bool:
        """
        Validate that the recipient identifier is properly formatted.

        Args:
            recipient: The recipient identifier to validate

        Returns:
            True if the recipient identifier is valid, False otherwise

        Raises:
            NotImplementedError: Must be implemented by concrete service classes
        """
        pass


# Legacy function maintained for backward compatibility
def send_notification(db: Session, user_id: str, title: str, body: str, channel: str = "in_app") -> None:
    """
    Legacy notification sending function.

    This function is maintained for backward compatibility with existing code.
    New code should use the NotificationOrchestrator with concrete service implementations.

    Args:
        db: Database session
        user_id: User identifier
        title: Notification title
        body: Notification body content
        channel: Notification channel (in_app, email, sms)
    """
    from app.db.models import Notification

    notif = Notification(
        user_id=user_id,
        title=title,
        body=body,
        channel=channel,
        sent_at=datetime.utcnow() if channel != "in_app" else None,
    )
    db.add(notif)
    db.commit()

    if channel == "email" and settings.sendgrid_api_key:
        _send_email(user_id, title, body)
    elif channel == "sms" and settings.twilio_account_sid:
        _send_sms(user_id, body)


def _send_email(user_id: str, subject: str, body: str) -> None:
    """Legacy email stub"""
    logger.info("Email notification queued for user=%s subject=%s", user_id, subject)


def _send_sms(user_id: str, body: str) -> None:
    """Legacy SMS stub"""
    logger.info("SMS notification queued for user=%s", user_id)
