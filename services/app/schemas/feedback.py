"""Pydantic schemas for feedback collection

**Validates: Requirements 21.1, 21.2**
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """
    Schema for creating new feedback.
    
    **Validates: Requirement 21.2** - Feedback schema SHALL include user_id,
    opportunity_id, feedback_type, and optional text comment.
    """
    opportunity_id: str = Field(
        ...,
        description="ID of the opportunity being rated",
        min_length=1
    )
    feedback_type: str = Field(
        ...,
        description="Type of feedback: relevant, not_relevant, ineligible, applied, ignored",
        min_length=1
    )
    comment: Optional[str] = Field(
        None,
        description="Optional text comment providing additional context",
        max_length=1000
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "opportunity_id": "opp-123",
                    "feedback_type": "relevant",
                    "comment": "Great match for my profile!"
                },
                {
                    "opportunity_id": "opp-456",
                    "feedback_type": "not_relevant",
                    "comment": None
                }
            ]
        }
    }


class ExperimentInfo(BaseModel):
    """Information about experiment variant assignment"""
    experiment_name: str
    variant_name: str


class FeedbackResponse(BaseModel):
    """
    Response after submitting feedback.
    
    Includes confirmation of submission and any associated experiment tracking.
    """
    user_id: str = Field(..., description="ID of the user who submitted feedback")
    opportunity_id: str = Field(..., description="ID of the opportunity rated")
    feedback_type: str = Field(..., description="Type of feedback submitted")
    comment: Optional[str] = Field(None, description="Optional comment text")
    feedback_count: int = Field(
        ...,
        description="Number of feedback records created (1 per active experiment)"
    )
    experiments: List[ExperimentInfo] = Field(
        default_factory=list,
        description="List of experiments this feedback is associated with"
    )
    submitted_at: str = Field(..., description="ISO timestamp of submission")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user-123",
                    "opportunity_id": "opp-456",
                    "feedback_type": "relevant",
                    "comment": "Perfect match!",
                    "feedback_count": 1,
                    "experiments": [
                        {
                            "experiment_name": "recommendation_algo_v2",
                            "variant_name": "treatment_a"
                        }
                    ],
                    "submitted_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    }


class FeedbackSummary(BaseModel):
    """Summary of feedback for analytics"""
    user_id: str
    feedback_by_type: Dict[str, int]
    total_feedback: int
