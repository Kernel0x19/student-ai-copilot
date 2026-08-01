"""
Tests for User Events Analytics Data Collection

This test suite validates the user event logging functionality for analytics
tracking including recommendations viewed, saved, and applied.

**Validates: Requirements 20.1, 20.2, 20.3, 21.1, 21.2**
"""

import pytest
from datetime import datetime
from unittest.mock import Mock
from sqlalchemy.orm import Session

from app.analytics.event_service import AnalyticsEventService, EventType
from app.db.models import (
    User,
    Opportunity,
    Application,
    UserEvent,
    UserExperiment,
    ExperimentVariant,
    Feedback
)


@pytest.fixture
def db_session():
    """Create a mock database session for testing"""
    session = Mock(spec=Session)
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.flush = Mock()
    return session


@pytest.fixture
def event_service(db_session):
    """Create an AnalyticsEventService instance"""
    return AnalyticsEventService(db_session)


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing"""
    return "user-123"


@pytest.fixture
def sample_opportunity_id():
    """Sample opportunity ID for testing"""
    return "opp-456"


class TestRecommendationViewed:
    """Test recommendation viewed event logging"""
    
    def test_log_recommendation_viewed_without_experiments(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test logging viewed event when user has no active experiments"""
        # Setup: No active experiments
        db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Execute
        result = event_service.log_recommendation_viewed(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id,
            match_score=0.85,
            context={"source": "dashboard"}
        )
        
        # Verify
        assert result["event_type"] == EventType.RECOMMENDATION_VIEWED
        assert result["user_id"] == sample_user_id
        assert result["opportunity_id"] == sample_opportunity_id
        assert result["match_score"] == 0.85
        assert result["event_count"] == 1
        assert db_session.add.called
        assert db_session.commit.called
    
    def test_log_recommendation_viewed_with_experiments(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test logging viewed event when user is in active experiments"""
        # Setup: User in one experiment
        mock_experiment = Mock()
        mock_experiment.experiment_name = "recommendation_algo_test"
        mock_experiment.variant_name = "treatment_a"
        db_session.query.return_value.filter.return_value.all.return_value = [mock_experiment]
        
        # Execute
        result = event_service.log_recommendation_viewed(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id,
            match_score=0.92
        )
        
        # Verify
        assert result["event_count"] == 1
        assert len(result["experiments"]) == 1
        assert result["experiments"][0]["experiment_name"] == "recommendation_algo_test"
        assert result["experiments"][0]["variant_name"] == "treatment_a"
        assert db_session.add.called
        assert db_session.commit.called


class TestRecommendationSaved:
    """Test recommendation saved event logging"""
    
    def test_log_recommendation_saved_creates_application(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test that saving a recommendation creates an application record"""
        # Setup: No experiments and no existing application
        # Mock the query chain for _get_user_experiments
        db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Mock the query chain for finding existing application
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = event_service.log_recommendation_saved(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id,
            source="search"
        )
        
        # Verify
        assert result["event_type"] == EventType.RECOMMENDATION_SAVED
        assert result["source"] == "search"
        assert result["event_count"] == 1
        assert db_session.add.called
        assert db_session.commit.called
    
    def test_log_recommendation_saved_updates_existing_application(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test that saving updates an existing application's saved status"""
        # Setup: Existing application
        mock_application = Mock()
        mock_application.id = "app-789"
        mock_application.saved = False
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_application
        db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Execute
        result = event_service.log_recommendation_saved(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id
        )
        
        # Verify
        assert mock_application.saved == True
        assert db_session.add.called  # Event record added
        assert db_session.commit.called


class TestRecommendationApplied:
    """Test recommendation applied event logging"""
    
    def test_log_recommendation_applied_creates_event_and_feedback(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test that applying creates both event and feedback records"""
        # Setup: User in experiment
        mock_experiment = Mock()
        mock_experiment.experiment_name = "algo_test"
        mock_experiment.variant_name = "control"
        db_session.query.return_value.filter.return_value.all.return_value = [mock_experiment]
        
        # Execute
        result = event_service.log_recommendation_applied(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id,
            application_id="app-999"
        )
        
        # Verify
        assert result["event_type"] == EventType.RECOMMENDATION_APPLIED
        assert result["application_id"] == "app-999"
        assert result["event_count"] == 1
        # Should create both UserEvent and Feedback records
        assert db_session.add.call_count >= 2
        assert db_session.commit.called


class TestRecommendationDismissed:
    """Test recommendation dismissed event logging"""
    
    def test_log_recommendation_dismissed_with_reason(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test dismissal logging with a reason"""
        # Setup: No experiments
        db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Execute
        result = event_service.log_recommendation_dismissed(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id,
            reason="not_interested"
        )
        
        # Verify
        assert result["event_type"] == EventType.RECOMMENDATION_DISMISSED
        assert result["reason"] == "not_interested"
        assert result["event_count"] == 1
        assert db_session.add.called
        assert db_session.commit.called


class TestFeedbackCollection:
    """Test explicit feedback collection"""
    
    def test_collect_feedback_without_experiments(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test collecting feedback when user has no active experiments"""
        # Setup: No experiments
        db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Execute
        result = event_service.collect_feedback(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id,
            feedback_type="relevant",
            comment="Great match!"
        )
        
        # Verify
        assert result["feedback_count"] == 1
        assert result["feedback_type"] == "relevant"
        assert db_session.add.called
        assert db_session.commit.called
    
    def test_collect_feedback_with_multiple_experiments(
        self, event_service, db_session, sample_user_id, sample_opportunity_id
    ):
        """Test that feedback is linked to all active experiments"""
        # Setup: User in two experiments
        mock_exp1 = Mock()
        mock_exp1.experiment_name = "exp1"
        mock_exp1.variant_name = "control"
        
        mock_exp2 = Mock()
        mock_exp2.experiment_name = "exp2"
        mock_exp2.variant_name = "treatment_b"
        
        db_session.query.return_value.filter.return_value.all.return_value = [mock_exp1, mock_exp2]
        
        # Execute
        result = event_service.collect_feedback(
            user_id=sample_user_id,
            opportunity_id=sample_opportunity_id,
            feedback_type="not_relevant"
        )
        
        # Verify
        assert result["feedback_count"] == 2
        assert len(result["experiments"]) == 2
        assert db_session.add.call_count == 2
        assert db_session.commit.called


class TestExperimentTracking:
    """Test experiment variant tracking in events"""
    
    def test_track_experiment_event(
        self, event_service, db_session, sample_user_id
    ):
        """Test tracking custom experiment events"""
        # Setup: User assigned to experiment
        mock_assignment = Mock()
        mock_assignment.experiment_name = "ui_test"
        mock_assignment.variant_name = "new_design"
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_assignment
        
        # Execute
        result = event_service.track_experiment_event(
            user_id=sample_user_id,
            experiment_name="ui_test",
            event_type="button_clicked",
            metadata={"button_id": "apply_now"}
        )
        
        # Verify
        assert result["event_type"] == "button_clicked"
        assert result["experiment_name"] == "ui_test"
        assert result["variant_name"] == "new_design"
        assert result["metadata"]["button_id"] == "apply_now"
    
    def test_track_experiment_event_user_not_assigned(
        self, event_service, db_session, sample_user_id
    ):
        """Test tracking event for unassigned user returns error"""
        # Setup: User not assigned to experiment
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = event_service.track_experiment_event(
            user_id=sample_user_id,
            experiment_name="nonexistent_exp",
            event_type="test_event"
        )
        
        # Verify
        assert "error" in result
        assert "not assigned" in result["error"]


class TestAnalyticsQueries:
    """Test analytics query methods"""
    
    def test_get_user_activity_summary(
        self, event_service, db_session, sample_user_id
    ):
        """Test retrieving user activity summary"""
        # Setup: Mock feedback and application data
        db_session.query.return_value.filter.return_value.group_by.return_value.all.return_value = [
            ("relevant", 5),
            ("applied", 2)
        ]
        
        # Execute
        result = event_service.get_user_activity_summary(user_id=sample_user_id)
        
        # Verify
        assert result["user_id"] == sample_user_id
        assert "feedback" in result
        assert "applications" in result
    
    def test_get_opportunity_engagement_metrics(
        self, event_service, db_session, sample_opportunity_id
    ):
        """Test retrieving opportunity engagement metrics"""
        # Setup: Mock engagement data
        db_session.query.return_value.filter.return_value.scalar.side_effect = [10, 5]
        db_session.query.return_value.filter.return_value.group_by.return_value.all.return_value = [
            ("applied", 3),
            ("relevant", 4)
        ]
        
        # Execute
        result = event_service.get_opportunity_engagement_metrics(
            opportunity_id=sample_opportunity_id
        )
        
        # Verify
        assert result["opportunity_id"] == sample_opportunity_id
        assert "total_applications" in result
        assert "saved_count" in result
        assert "feedback" in result
        assert "engagement_rate" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
