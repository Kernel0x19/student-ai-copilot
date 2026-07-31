"""
Unit Tests for Notification Database Models

Tests the database models for notification preferences, history, and device tokens.

**Validates: Requirements 10.1, 11.1, 12.1, 13.1**
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    User,
    UserRole,
    NotificationPreference,
    NotificationHistory,
    DeviceToken,
    Base
)


@pytest.fixture
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        id="test-user-123",
        email="test@example.com",
        phone_number="+1234567890",
        role=UserRole.STUDENT
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestNotificationPreference:
    """Test NotificationPreference model"""
    
    def test_create_notification_preference(self, db_session, test_user):
        """Test creating a notification preference record"""
        pref = NotificationPreference(
            user_id=test_user.id,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True,
            deadline_reminders=True,
            new_matches=True,
            status_updates=True,
            deadline_changes=True,
            phone_verified=False
        )
        db_session.add(pref)
        db_session.commit()
        
        # Verify it was created
        saved_pref = db_session.query(NotificationPreference).filter_by(user_id=test_user.id).first()
        assert saved_pref is not None
        assert saved_pref.user_id == test_user.id
        assert saved_pref.email_enabled is True
        assert saved_pref.sms_enabled is False
        assert saved_pref.push_enabled is True
        assert saved_pref.deadline_reminders is True
        assert saved_pref.new_matches is True
        assert saved_pref.status_updates is True
        assert saved_pref.deadline_changes is True
        assert saved_pref.phone_verified is False
    
    def test_notification_preference_defaults(self, db_session, test_user):
        """Test that notification preferences have correct default values"""
        pref = NotificationPreference(user_id=test_user.id)
        db_session.add(pref)
        db_session.commit()
        
        saved_pref = db_session.query(NotificationPreference).filter_by(user_id=test_user.id).first()
        assert saved_pref.email_enabled is True  # Default: enabled
        assert saved_pref.sms_enabled is False  # Default: disabled
        assert saved_pref.push_enabled is True  # Default: enabled
        assert saved_pref.deadline_reminders is True
        assert saved_pref.new_matches is True
        assert saved_pref.status_updates is True
        assert saved_pref.deadline_changes is True
        assert saved_pref.phone_verified is False
    
    def test_notification_preference_unique_per_user(self, db_session, test_user):
        """Test that each user can have only one notification preference record"""
        pref1 = NotificationPreference(user_id=test_user.id)
        db_session.add(pref1)
        db_session.commit()
        
        # Try to create a second preference for the same user
        pref2 = NotificationPreference(user_id=test_user.id)
        db_session.add(pref2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_notification_preference_timestamps(self, db_session, test_user):
        """Test that created_at and updated_at timestamps are set"""
        pref = NotificationPreference(user_id=test_user.id)
        db_session.add(pref)
        db_session.commit()
        
        saved_pref = db_session.query(NotificationPreference).filter_by(user_id=test_user.id).first()
        assert saved_pref.created_at is not None
        assert saved_pref.updated_at is not None
        assert isinstance(saved_pref.created_at, datetime)
        assert isinstance(saved_pref.updated_at, datetime)
    
    def test_update_notification_preference(self, db_session, test_user):
        """Test updating notification preferences"""
        pref = NotificationPreference(
            user_id=test_user.id,
            email_enabled=True,
            sms_enabled=False
        )
        db_session.add(pref)
        db_session.commit()
        
        # Update preferences
        pref.email_enabled = False
        pref.sms_enabled = True
        pref.phone_verified = True
        db_session.commit()
        
        # Verify updates
        saved_pref = db_session.query(NotificationPreference).filter_by(user_id=test_user.id).first()
        assert saved_pref.email_enabled is False
        assert saved_pref.sms_enabled is True
        assert saved_pref.phone_verified is True


class TestNotificationHistory:
    """Test NotificationHistory model"""
    
    def test_create_notification_history(self, db_session, test_user):
        """Test creating a notification history record"""
        history = NotificationHistory(
            user_id=test_user.id,
            notification_type="deadline_reminder",
            channel="email",
            recipient="test@example.com",
            success=True,
            message_id="msg_123"
        )
        db_session.add(history)
        db_session.commit()
        
        # Verify it was created
        saved = db_session.query(NotificationHistory).filter_by(user_id=test_user.id).first()
        assert saved is not None
        assert saved.user_id == test_user.id
        assert saved.notification_type == "deadline_reminder"
        assert saved.channel == "email"
        assert saved.recipient == "test@example.com"
        assert saved.success is True
        assert saved.message_id == "msg_123"
        assert saved.error is None
    
    def test_notification_history_with_error(self, db_session, test_user):
        """Test logging a failed notification"""
        history = NotificationHistory(
            user_id=test_user.id,
            notification_type="new_match",
            channel="sms",
            recipient="+1234567890",
            success=False,
            error="Invalid phone number"
        )
        db_session.add(history)
        db_session.commit()
        
        saved = db_session.query(NotificationHistory).filter_by(user_id=test_user.id).first()
        assert saved.success is False
        assert saved.error == "Invalid phone number"
        assert saved.message_id is None
    
    def test_notification_history_supports_multiple_channels(self, db_session, test_user):
        """Test logging notifications across different channels"""
        email_notif = NotificationHistory(
            user_id=test_user.id,
            notification_type="deadline_reminder",
            channel="email",
            recipient="test@example.com",
            success=True
        )
        sms_notif = NotificationHistory(
            user_id=test_user.id,
            notification_type="deadline_reminder",
            channel="sms",
            recipient="+1234567890",
            success=True
        )
        push_notif = NotificationHistory(
            user_id=test_user.id,
            notification_type="deadline_reminder",
            channel="push",
            recipient="device_token_123",
            success=True
        )
        
        db_session.add_all([email_notif, sms_notif, push_notif])
        db_session.commit()
        
        # Verify all channels were logged
        all_notifs = db_session.query(NotificationHistory).filter_by(user_id=test_user.id).all()
        assert len(all_notifs) == 3
        channels = {n.channel for n in all_notifs}
        assert channels == {"email", "sms", "push"}
    
    def test_notification_history_supports_all_types(self, db_session, test_user):
        """Test logging all notification types"""
        types = ["deadline_reminder", "application_status_change", "new_match", "deadline_change"]
        
        for notif_type in types:
            history = NotificationHistory(
                user_id=test_user.id,
                notification_type=notif_type,
                channel="email",
                recipient="test@example.com",
                success=True
            )
            db_session.add(history)
        
        db_session.commit()
        
        # Verify all types were logged
        all_notifs = db_session.query(NotificationHistory).filter_by(user_id=test_user.id).all()
        assert len(all_notifs) == 4
        logged_types = {n.notification_type for n in all_notifs}
        assert logged_types == set(types)
    
    def test_notification_history_timestamp(self, db_session, test_user):
        """Test that sent_at timestamp is automatically set"""
        history = NotificationHistory(
            user_id=test_user.id,
            notification_type="deadline_reminder",
            channel="email",
            recipient="test@example.com",
            success=True
        )
        db_session.add(history)
        db_session.commit()
        
        saved = db_session.query(NotificationHistory).filter_by(user_id=test_user.id).first()
        assert saved.sent_at is not None
        assert isinstance(saved.sent_at, datetime)
    
    def test_query_notification_history_by_channel(self, db_session, test_user):
        """Test querying notification history by channel (indexed field)"""
        # Create multiple notifications
        for i in range(5):
            history = NotificationHistory(
                user_id=test_user.id,
                notification_type="deadline_reminder",
                channel="email" if i % 2 == 0 else "sms",
                recipient="test@example.com",
                success=True
            )
            db_session.add(history)
        db_session.commit()
        
        # Query by channel
        email_notifs = db_session.query(NotificationHistory).filter_by(
            user_id=test_user.id,
            channel="email"
        ).all()
        
        assert len(email_notifs) == 3
        assert all(n.channel == "email" for n in email_notifs)


class TestDeviceToken:
    """Test DeviceToken model"""
    
    def test_create_device_token(self, db_session, test_user):
        """Test creating a device token record"""
        token = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_abc123",
            platform="android",
            is_active=True
        )
        db_session.add(token)
        db_session.commit()
        
        # Verify it was created
        saved = db_session.query(DeviceToken).filter_by(user_id=test_user.id).first()
        assert saved is not None
        assert saved.user_id == test_user.id
        assert saved.token == "fcm_token_abc123"
        assert saved.platform == "android"
        assert saved.is_active is True
    
    def test_device_token_supports_multiple_platforms(self, db_session, test_user):
        """Test storing device tokens for different platforms"""
        platforms = ["ios", "android", "web"]
        
        for platform in platforms:
            token = DeviceToken(
                user_id=test_user.id,
                token=f"fcm_token_{platform}",
                platform=platform,
                is_active=True
            )
            db_session.add(token)
        
        db_session.commit()
        
        # Verify all platforms are stored
        all_tokens = db_session.query(DeviceToken).filter_by(user_id=test_user.id).all()
        assert len(all_tokens) == 3
        stored_platforms = {t.platform for t in all_tokens}
        assert stored_platforms == set(platforms)
    
    def test_device_token_unique_constraint(self, db_session, test_user):
        """Test that device tokens must be unique"""
        token1 = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_duplicate",
            platform="android",
            is_active=True
        )
        db_session.add(token1)
        db_session.commit()
        
        # Try to create another token with the same token string
        token2 = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_duplicate",
            platform="ios",
            is_active=True
        )
        db_session.add(token2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_device_token_deactivation(self, db_session, test_user):
        """Test deactivating a device token"""
        token = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_xyz",
            platform="android",
            is_active=True
        )
        db_session.add(token)
        db_session.commit()
        
        # Deactivate token
        token.is_active = False
        db_session.commit()
        
        # Verify deactivation
        saved = db_session.query(DeviceToken).filter_by(token="fcm_token_xyz").first()
        assert saved.is_active is False
    
    def test_device_token_timestamps(self, db_session, test_user):
        """Test that created_at and updated_at timestamps are set"""
        token = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_timestamps",
            platform="android",
            is_active=True
        )
        db_session.add(token)
        db_session.commit()
        
        saved = db_session.query(DeviceToken).filter_by(user_id=test_user.id).first()
        assert saved.created_at is not None
        assert saved.updated_at is not None
        assert isinstance(saved.created_at, datetime)
        assert isinstance(saved.updated_at, datetime)
    
    def test_query_active_device_tokens(self, db_session, test_user):
        """Test querying only active device tokens"""
        # Create active and inactive tokens
        active_token = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_active",
            platform="android",
            is_active=True
        )
        inactive_token = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_inactive",
            platform="ios",
            is_active=False
        )
        
        db_session.add_all([active_token, inactive_token])
        db_session.commit()
        
        # Query only active tokens
        active_tokens = db_session.query(DeviceToken).filter_by(
            user_id=test_user.id,
            is_active=True
        ).all()
        
        assert len(active_tokens) == 1
        assert active_tokens[0].token == "fcm_token_active"
    
    def test_user_can_have_multiple_device_tokens(self, db_session, test_user):
        """Test that a user can have multiple device tokens (multiple devices)"""
        token1 = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_device1",
            platform="android",
            is_active=True
        )
        token2 = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_device2",
            platform="android",
            is_active=True
        )
        token3 = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_device3",
            platform="ios",
            is_active=True
        )
        
        db_session.add_all([token1, token2, token3])
        db_session.commit()
        
        # Verify all tokens are stored
        all_tokens = db_session.query(DeviceToken).filter_by(user_id=test_user.id).all()
        assert len(all_tokens) == 3


class TestNotificationModelsIntegration:
    """Test integration between notification models"""
    
    def test_full_notification_workflow(self, db_session, test_user):
        """Test complete notification workflow using all three models"""
        # Step 1: Set user preferences
        pref = NotificationPreference(
            user_id=test_user.id,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True,
            deadline_reminders=True
        )
        db_session.add(pref)
        
        # Step 2: Register device token
        device = DeviceToken(
            user_id=test_user.id,
            token="fcm_token_workflow",
            platform="android",
            is_active=True
        )
        db_session.add(device)
        
        # Step 3: Send notification and log it
        history = NotificationHistory(
            user_id=test_user.id,
            notification_type="deadline_reminder",
            channel="push",
            recipient="fcm_token_workflow",
            success=True,
            message_id="msg_workflow_123"
        )
        db_session.add(history)
        
        db_session.commit()
        
        # Verify all records are connected
        saved_pref = db_session.query(NotificationPreference).filter_by(user_id=test_user.id).first()
        saved_device = db_session.query(DeviceToken).filter_by(user_id=test_user.id).first()
        saved_history = db_session.query(NotificationHistory).filter_by(user_id=test_user.id).first()
        
        assert saved_pref is not None
        assert saved_device is not None
        assert saved_history is not None
        assert saved_pref.push_enabled is True
        assert saved_device.token == saved_history.recipient


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
