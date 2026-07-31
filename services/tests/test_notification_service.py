"""
Unit Tests for Notification Service Abstractions

Tests the abstract base classes, enums, and interfaces for notification services.

**Validates: Requirements 10.1, 11.1, 12.1**
"""

import pytest
from typing import Any, Dict

from app.notifications.service import (
    NotificationChannel,
    NotificationService,
    NotificationType,
)


class ConcreteNotificationService(NotificationService):
    """
    Concrete implementation of NotificationService for testing.
    This simulates a real notification service (e.g., email, SMS, push).
    """

    def __init__(self):
        self.sent_messages = []
        self.should_fail = False
        self.validation_result = True

    async def send(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Test implementation of send method"""
        if self.should_fail:
            return {
                "success": False,
                "error": "Simulated send failure",
            }

        self.sent_messages.append({"recipient": recipient, "message": message})
        return {
            "success": True,
            "message_id": f"test_msg_{len(self.sent_messages)}",
        }

    async def validate_recipient(self, recipient: str) -> bool:
        """Test implementation of validate_recipient method"""
        return self.validation_result


class TestNotificationType:
    """Test NotificationType enum"""

    def test_notification_type_values(self):
        """Test that all expected notification types are defined"""
        assert NotificationType.DEADLINE_REMINDER.value == "deadline_reminder"
        assert NotificationType.APPLICATION_STATUS.value == "application_status_change"
        assert NotificationType.NEW_MATCH.value == "new_match"
        assert NotificationType.DEADLINE_CHANGE.value == "deadline_change"

    def test_notification_type_membership(self):
        """Test that we can check notification type membership"""
        types = [t.value for t in NotificationType]
        assert "deadline_reminder" in types
        assert "application_status_change" in types
        assert "new_match" in types
        assert "deadline_change" in types

    def test_notification_type_count(self):
        """Test that we have exactly 4 notification types"""
        assert len(NotificationType) == 4


class TestNotificationChannel:
    """Test NotificationChannel enum"""

    def test_notification_channel_values(self):
        """Test that all expected channels are defined"""
        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.SMS.value == "sms"
        assert NotificationChannel.PUSH.value == "push"
        assert NotificationChannel.IN_APP.value == "in_app"

    def test_notification_channel_membership(self):
        """Test that we can check channel membership"""
        channels = [c.value for c in NotificationChannel]
        assert "email" in channels
        assert "sms" in channels
        assert "push" in channels
        assert "in_app" in channels

    def test_notification_channel_count(self):
        """Test that we have exactly 4 notification channels"""
        assert len(NotificationChannel) == 4


class TestNotificationServiceInterface:
    """Test NotificationService abstract base class and interface"""

    @pytest.mark.asyncio
    async def test_concrete_implementation_can_be_instantiated(self):
        """Test that concrete implementations of the abstract base can be created"""
        service = ConcreteNotificationService()
        assert isinstance(service, NotificationService)

    @pytest.mark.asyncio
    async def test_send_method_returns_expected_structure(self):
        """Test that send method returns correctly structured response on success"""
        service = ConcreteNotificationService()
        result = await service.send(
            "test@example.com", {"subject": "Test", "body": "Test message"}
        )

        assert "success" in result
        assert result["success"] is True
        assert "message_id" in result
        assert result["message_id"] == "test_msg_1"

    @pytest.mark.asyncio
    async def test_send_method_handles_failure(self):
        """Test that send method returns error information on failure"""
        service = ConcreteNotificationService()
        service.should_fail = True

        result = await service.send("test@example.com", {"body": "Test"})

        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "Simulated send failure" in result["error"]

    @pytest.mark.asyncio
    async def test_send_method_tracks_messages(self):
        """Test that multiple send calls are tracked correctly"""
        service = ConcreteNotificationService()

        await service.send("user1@example.com", {"body": "Message 1"})
        await service.send("user2@example.com", {"body": "Message 2"})
        await service.send("user3@example.com", {"body": "Message 3"})

        assert len(service.sent_messages) == 3
        assert service.sent_messages[0]["recipient"] == "user1@example.com"
        assert service.sent_messages[1]["recipient"] == "user2@example.com"
        assert service.sent_messages[2]["recipient"] == "user3@example.com"

    @pytest.mark.asyncio
    async def test_validate_recipient_returns_boolean(self):
        """Test that validate_recipient returns boolean value"""
        service = ConcreteNotificationService()

        # Test valid recipient
        is_valid = await service.validate_recipient("test@example.com")
        assert isinstance(is_valid, bool)
        assert is_valid is True

        # Test invalid recipient
        service.validation_result = False
        is_valid = await service.validate_recipient("invalid")
        assert isinstance(is_valid, bool)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_send_supports_different_message_structures(self):
        """Test that send method can handle different message structures for different channels"""
        service = ConcreteNotificationService()

        # Email structure
        email_result = await service.send(
            "test@example.com", {"subject": "Test Subject", "body": "Test body", "html": "<p>Test</p>"}
        )
        assert email_result["success"]

        # SMS structure
        sms_result = await service.send("+1234567890", {"body": "Short message"})
        assert sms_result["success"]

        # Push notification structure
        push_result = await service.send(
            "device_token_123",
            {"title": "Push Title", "body": "Push body", "data": {"action": "view"}},
        )
        assert push_result["success"]

        # All messages should be tracked
        assert len(service.sent_messages) == 3

    def test_cannot_instantiate_abstract_base_directly(self):
        """Test that NotificationService cannot be instantiated directly"""
        with pytest.raises(TypeError) as exc_info:
            NotificationService()

        assert "abstract" in str(exc_info.value).lower()


class TestNotificationServiceContract:
    """Test that the NotificationService contract is enforced"""

    def test_concrete_class_must_implement_send(self):
        """Test that concrete implementations must override send method"""

        class IncompleteService(NotificationService):
            async def validate_recipient(self, recipient: str) -> bool:
                return True

        with pytest.raises(TypeError):
            IncompleteService()

    def test_concrete_class_must_implement_validate_recipient(self):
        """Test that concrete implementations must override validate_recipient method"""

        class IncompleteService(NotificationService):
            async def send(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
                return {"success": True}

        with pytest.raises(TypeError):
            IncompleteService()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
