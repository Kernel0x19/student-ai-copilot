"""Unit tests for Notification Services (Email, SMS, Push, Orchestrator, Deadline Monitor)

Validates: Requirements 10.1-10.7, 11.1-11.7, 12.1-12.7, 13.1-13.7
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.notifications.email import EmailNotificationService
from app.notifications.sms import SMSNotificationService
from app.notifications.push import PushNotificationService
from app.notifications.orchestrator import NotificationOrchestrator
from app.notifications.deadline_monitor import DeadlineMonitor
from app.notifications.service import NotificationType, NotificationChannel
from app.db.models import User, Application, Opportunity, AuditLog, NotificationPreference


@pytest.fixture
def mock_db():
    return Mock()


@pytest.mark.asyncio
async def test_email_service_send_and_validation():
    service = EmailNotificationService()
    assert await service.validate_recipient("student@example.com") is True
    assert await service.validate_recipient("invalid-email") is False
    
    res = await service.send("student@example.com", {"subject": "Test", "body": "Hello"})
    assert res['success'] is True
    assert res['recipient'] == "student@example.com"


@pytest.mark.asyncio
async def test_sms_service_send_and_truncation():
    service = SMSNotificationService()
    assert await service.validate_recipient("+15005550006") is True
    assert await service.validate_recipient("123") is False
    
    truncated = service.truncate_message("A" * 200, max_length=160)
    assert len(truncated) == 160
    assert truncated.endswith("...")
    
    res = await service.send("+15005550006", {"body": "Short text"})
    assert res['success'] is True


@pytest.mark.asyncio
async def test_push_service_send_and_deep_link():
    service = PushNotificationService()
    assert await service.validate_recipient("fcm_token_1234567890_valid") is True
    assert await service.validate_recipient("short") is False
    
    link = service.generate_deep_link(opportunity_id="opp-123", screen="opportunity")
    assert link == "edupilot://opportunity/opp-123"
    
    res = await service.send("fcm_token_1234567890_valid", {"title": "Title", "body": "Body", "opportunity_id": "opp-123"})
    assert res['success'] is True
    assert res['deep_link'] == link


@pytest.mark.asyncio
async def test_notification_orchestrator(mock_db):
    user = Mock(spec=User)
    user.id = "user-1"
    user.email = "test@example.com"
    user.phone_number = "+15005550006"
    user.device_token = "fcm_token_1234567890_valid"
    
    # Query for NotificationPreference returns None (default channel settings), query for User returns user
    mock_db.query.return_value.filter_by.side_effect = lambda **kwargs: Mock(first=lambda: user if 'id' in kwargs else None)
    
    orchestrator = NotificationOrchestrator(mock_db)
    res = await orchestrator.send_notification(
        user_id="user-1",
        notification_type=NotificationType.DEADLINE_REMINDER,
        title="Deadline",
        body="Deadline soon"
    )
    
    assert res['user_id'] == "user-1"
    assert "email" in res['channels_attempted']
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_deadline_monitor(mock_db):
    app = Mock(spec=Application)
    app.id = "app-100"
    app.user_id = "user-1"
    app.opportunity_id = "opp-200"
    app.saved = True
    app.state = "in_progress"
    
    opp = Mock(spec=Opportunity)
    opp.id = "opp-200"
    opp.title = "Engineering Scholarship"
    opp.deadline = datetime.utcnow() + timedelta(days=7)
    
    user = Mock(spec=User)
    user.id = "user-1"
    user.email = "test@example.com"

    # Mock query responses
    def filter_side_effect(*args, **kwargs):
        mock_filter = Mock()
        mock_filter.all.return_value = [app]
        mock_filter.first.return_value = None  # No prior AuditLog
        return mock_filter

    def filter_by_side_effect(**kwargs):
        mock_fb = Mock()
        if kwargs.get('id') == "opp-200":
            mock_fb.first.return_value = opp
        elif kwargs.get('id') == "user-1":
            mock_fb.first.return_value = user
        else:
            mock_fb.first.return_value = None
        return mock_fb

    mock_db.query.return_value.filter.side_effect = filter_side_effect
    mock_db.query.return_value.filter_by.side_effect = filter_by_side_effect

    monitor = DeadlineMonitor(mock_db)
    res = await monitor.scan_and_notify_deadlines()
    
    assert res['reminders_sent'] == 1
    assert mock_db.add.called
