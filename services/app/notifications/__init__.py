"""
Notification System Package

This package provides abstractions and implementations for multi-channel
notification delivery across email, SMS, and push notification channels.
"""

from .service import (
    NotificationChannel,
    NotificationService,
    NotificationType,
    send_notification,
)

__all__ = [
    "NotificationService",
    "NotificationType",
    "NotificationChannel",
    "send_notification",
]
