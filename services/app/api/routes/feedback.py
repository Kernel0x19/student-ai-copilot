"""API endpoints for feedback collection

This module provides endpoints for collecting explicit user feedback on recommendations
and opportunities, supporting the analytics and A/B testing infrastructure.

**Validates: Requirements 21.1, 21.2, 21.3, 21.4, 21.7**
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.analytics.event_service import AnalyticsEventService
from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit explicit feedback on a recommendation or opportunity.
    
    This endpoint allows users to rate the relevance and quality of recommendations,
    which helps improve the recommendation algorithm and provides data for A/B testing
    analysis.
    
    **Supported Feedback Types:**
    - `relevant`: The recommendation was useful and appropriate
    - `not_relevant`: The recommendation was not useful or appropriate  
    - `ineligible`: The user is not eligible for this opportunity
    - `applied`: The user applied to this opportunity
    - `ignored`: The user dismissed/ignored this opportunity
    
    **Requirements:**
    - 21.1: Expose `/api/v1/feedback` endpoint accepting feedback submissions
    - 21.2: Feedback schema includes user_id, opportunity_id, feedback_type, and optional comment
    - 21.4: Associate feedback with active experiment variants when applicable
    - 21.7: Feedback collection UI appears after users interact with recommendations
    
    Args:
        feedback: Feedback submission containing opportunity_id, type, and optional comment
        db: Database session (injected)
        current_user: Authenticated user (injected)
    
    Returns:
        FeedbackResponse with submission details including experiment tracking
    """
    # Validate feedback type
    valid_types = {"relevant", "not_relevant", "ineligible", "applied", "ignored"}
    if feedback.feedback_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create event service
    event_service = AnalyticsEventService(db)
    
    try:
        # Collect feedback with experiment tracking
        # Requirement 21.4: Associate feedback with active experiment variants
        result = event_service.collect_feedback(
            user_id=current_user.id,
            opportunity_id=feedback.opportunity_id,
            feedback_type=feedback.feedback_type,
            comment=feedback.comment
        )
        
        return FeedbackResponse(
            user_id=current_user.id,
            opportunity_id=feedback.opportunity_id,
            feedback_type=feedback.feedback_type,
            comment=feedback.comment,
            feedback_count=result["feedback_count"],
            experiments=result.get("experiments", []),
            submitted_at=result["timestamp"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/user/summary")
def get_user_feedback_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get summary of feedback submitted by the current user.
    
    Returns counts of feedback by type for the authenticated user.
    
    Args:
        db: Database session (injected)
        current_user: Authenticated user (injected)
    
    Returns:
        Dictionary with feedback counts by type
    """
    from app.db.models import Feedback
    from sqlalchemy import func
    
    # Get feedback counts by type for this user
    feedback_summary = db.query(
        Feedback.feedback_type,
        func.count(Feedback.id)
    ).filter(
        Feedback.user_id == current_user.id
    ).group_by(Feedback.feedback_type).all()
    
    return {
        "user_id": current_user.id,
        "feedback_by_type": {
            feedback_type: count 
            for feedback_type, count in feedback_summary
        },
        "total_feedback": sum(count for _, count in feedback_summary)
    }


@router.get("/opportunity/{opportunity_id}")
def get_opportunity_feedback(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's feedback for a specific opportunity (if any).
    
    Returns the user's feedback record for the given opportunity, or null if
    no feedback has been submitted.
    
    Args:
        opportunity_id: ID of the opportunity
        db: Database session (injected)
        current_user: Authenticated user (injected)
    
    Returns:
        Feedback record or null
    """
    from app.db.models import Feedback
    
    feedback = db.query(Feedback).filter(
        Feedback.user_id == current_user.id,
        Feedback.opportunity_id == opportunity_id
    ).order_by(Feedback.created_at.desc()).first()
    
    if not feedback:
        return {"feedback": None}
    
    return {
        "feedback": {
            "opportunity_id": feedback.opportunity_id,
            "feedback_type": feedback.feedback_type,
            "comment": feedback.comment,
            "experiment_name": feedback.experiment_name,
            "variant_name": feedback.variant_name,
            "submitted_at": feedback.created_at.isoformat()
        }
    }
