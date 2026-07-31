"""
Tests for Feedback Collection API

This test suite validates the feedback collection endpoints that support
analytics tracking and A/B testing analysis.

**Validates: Requirements 21.1, 21.2, 21.3, 21.4, 21.7**
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_current_user, get_db
from app.db.models import User, UserRole


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return Mock()


@pytest.fixture
def mock_user():
    """Create a mock authenticated user"""
    user = Mock(spec=User)
    user.id = "user-123"
    user.email = "test@example.com"
    user.role = UserRole.STUDENT
    return user


@pytest.fixture
def client(mock_db, mock_user):
    """Create a test client with dependency overrides"""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestFeedbackSubmission:
    """Test feedback submission endpoint"""
    
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    @patch("app.api.routes.feedback.AnalyticsEventService")
    def test_submit_feedback_success(
        self,
        mock_event_service_class,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db
    ):
        """Test successful feedback submission
        
        **Validates: Requirements 21.1, 21.2**
        """
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Mock event service
        mock_event_service = Mock()
        mock_event_service.collect_feedback.return_value = {
            "feedback_count": 1,
            "user_id": "user-123",
            "opportunity_id": "opp-456",
            "feedback_type": "relevant",
            "experiments": [
                {
                    "experiment_name": "rec_algo_v2",
                    "variant_name": "treatment_a"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        mock_event_service_class.return_value = mock_event_service
        
        # Make request
        response = client.post(
            "/api/v1/feedback/",
            json={
                "opportunity_id": "opp-456",
                "feedback_type": "relevant",
                "comment": "Great match!"
            }
        )
        
        # Verify
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == "user-123"
        assert data["opportunity_id"] == "opp-456"
        assert data["feedback_type"] == "relevant"
        assert data["comment"] == "Great match!"
        assert data["feedback_count"] == 1
        assert len(data["experiments"]) == 1
        assert data["experiments"][0]["experiment_name"] == "rec_algo_v2"
        
        # Verify service was called correctly
        mock_event_service.collect_feedback.assert_called_once_with(
            user_id="user-123",
            opportunity_id="opp-456",
            feedback_type="relevant",
            comment="Great match!"
        )
    
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    def test_submit_feedback_invalid_type(
        self,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db
    ):
        """Test feedback submission with invalid feedback type"""
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Make request with invalid type
        response = client.post(
            "/api/v1/feedback/",
            json={
                "opportunity_id": "opp-456",
                "feedback_type": "invalid_type",
                "comment": None
            }
        )
        
        # Verify
        assert response.status_code == 400
        assert "Invalid feedback_type" in response.json()["detail"]
    
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    @patch("app.api.routes.feedback.AnalyticsEventService")
    def test_submit_feedback_without_comment(
        self,
        mock_event_service_class,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db
    ):
        """Test feedback submission without optional comment
        
        **Validates: Requirement 21.2** - comment is optional
        """
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        mock_event_service = Mock()
        mock_event_service.collect_feedback.return_value = {
            "feedback_count": 1,
            "user_id": "user-123",
            "opportunity_id": "opp-789",
            "feedback_type": "not_relevant",
            "experiments": [],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        mock_event_service_class.return_value = mock_event_service
        
        # Make request without comment
        response = client.post(
            "/api/v1/feedback/",
            json={
                "opportunity_id": "opp-789",
                "feedback_type": "not_relevant"
            }
        )
        
        # Verify
        assert response.status_code == 201
        data = response.json()
        assert data["comment"] is None
        
        # Verify service was called with None comment
        mock_event_service.collect_feedback.assert_called_once_with(
            user_id="user-123",
            opportunity_id="opp-789",
            feedback_type="not_relevant",
            comment=None
        )
    
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    @patch("app.api.routes.feedback.AnalyticsEventService")
    def test_submit_feedback_with_experiment_tracking(
        self,
        mock_event_service_class,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db
    ):
        """Test that feedback is associated with active experiments
        
        **Validates: Requirement 21.4** - Associate feedback with active experiment variants
        """
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Mock user in multiple experiments
        mock_event_service = Mock()
        mock_event_service.collect_feedback.return_value = {
            "feedback_count": 2,
            "user_id": "user-123",
            "opportunity_id": "opp-999",
            "feedback_type": "applied",
            "experiments": [
                {
                    "experiment_name": "exp1",
                    "variant_name": "control"
                },
                {
                    "experiment_name": "exp2",
                    "variant_name": "treatment_b"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        mock_event_service_class.return_value = mock_event_service
        
        # Make request
        response = client.post(
            "/api/v1/feedback/",
            json={
                "opportunity_id": "opp-999",
                "feedback_type": "applied",
                "comment": "Applied successfully!"
            }
        )
        
        # Verify
        assert response.status_code == 201
        data = response.json()
        assert data["feedback_count"] == 2
        assert len(data["experiments"]) == 2
        assert data["experiments"][0]["experiment_name"] == "exp1"
        assert data["experiments"][1]["experiment_name"] == "exp2"


class TestFeedbackRetrieval:
    """Test feedback retrieval endpoints"""
    
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    def test_get_user_feedback_summary(
        self,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db
    ):
        """Test retrieving user's feedback summary"""
        # Setup mocks
        mock_get_user.return_value = mock_user
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.all.return_value = [
            ("relevant", 5),
            ("not_relevant", 2),
            ("applied", 3)
        ]
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.get("/api/v1/feedback/user/summary")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user-123"
        assert data["feedback_by_type"]["relevant"] == 5
        assert data["feedback_by_type"]["not_relevant"] == 2
        assert data["feedback_by_type"]["applied"] == 3
        assert data["total_feedback"] == 10
    
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    def test_get_opportunity_feedback(
        self,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db
    ):
        """Test retrieving user's feedback for a specific opportunity"""
        # Setup mocks
        mock_get_user.return_value = mock_user
        
        # Mock feedback record
        mock_feedback = Mock()
        mock_feedback.opportunity_id = "opp-123"
        mock_feedback.feedback_type = "relevant"
        mock_feedback.comment = "Perfect match"
        mock_feedback.experiment_name = "exp1"
        mock_feedback.variant_name = "control"
        mock_feedback.created_at = datetime(2024, 1, 15, 10, 30, 0)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = mock_feedback
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.get("/api/v1/feedback/opportunity/opp-123")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["feedback"]["opportunity_id"] == "opp-123"
        assert data["feedback"]["feedback_type"] == "relevant"
        assert data["feedback"]["comment"] == "Perfect match"
        assert data["feedback"]["experiment_name"] == "exp1"
    
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    def test_get_opportunity_feedback_not_found(
        self,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db
    ):
        """Test retrieving feedback when user hasn't provided any"""
        # Setup mocks
        mock_get_user.return_value = mock_user
        
        # Mock no feedback found
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.get("/api/v1/feedback/opportunity/opp-nonexistent")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["feedback"] is None


class TestFeedbackTypes:
    """Test all supported feedback types"""
    
    @pytest.mark.parametrize("feedback_type", [
        "relevant",
        "not_relevant",
        "ineligible",
        "applied",
        "ignored"
    ])
    @patch("app.api.routes.feedback.get_db")
    @patch("app.api.routes.feedback.get_current_user")
    @patch("app.api.routes.feedback.AnalyticsEventService")
    def test_all_feedback_types_accepted(
        self,
        mock_event_service_class,
        mock_get_user,
        mock_get_db,
        client,
        mock_user,
        mock_db,
        feedback_type
    ):
        """Test that all valid feedback types are accepted
        
        **Validates: Requirement 21.2** - feedback_type values
        """
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        mock_event_service = Mock()
        mock_event_service.collect_feedback.return_value = {
            "feedback_count": 1,
            "user_id": "user-123",
            "opportunity_id": "opp-test",
            "feedback_type": feedback_type,
            "experiments": [],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        mock_event_service_class.return_value = mock_event_service
        
        # Make request
        response = client.post(
            "/api/v1/feedback/",
            json={
                "opportunity_id": "opp-test",
                "feedback_type": feedback_type
            }
        )
        
        # Verify
        assert response.status_code == 201
        assert response.json()["feedback_type"] == feedback_type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
