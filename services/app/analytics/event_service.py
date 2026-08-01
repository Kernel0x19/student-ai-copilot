"""Analytics Event Logging Service

This module provides event logging functionality for tracking user actions,
including recommendations viewed, saved, and applied actions. These events
are used for analytics, A/B testing analysis, and improving recommendation
accuracy.

**Validates: Requirements 20.1, 20.2, 20.3, 21.1, 21.2**
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.db.models import (
    UserExperiment,
    Feedback,
    Application,
    Opportunity,
    User,
    UserEvent
)


class EventType:
    """Event type constants for analytics tracking"""
    RECOMMENDATION_VIEWED = "recommendation_viewed"
    RECOMMENDATION_SAVED = "recommendation_saved"
    RECOMMENDATION_APPLIED = "recommendation_applied"
    RECOMMENDATION_DISMISSED = "recommendation_dismissed"
    PROFILE_UPDATED = "profile_updated"
    DOCUMENT_UPLOADED = "document_uploaded"


class AnalyticsEventService:
    """
    Service for logging user actions and events for analytics tracking.
    
    This service provides centralized event logging functionality that supports:
    - User action tracking (views, saves, applications)
    - Experiment variant association
    - Feedback collection integration
    - Analytics aggregation and reporting
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log_recommendation_viewed(
        self,
        user_id: str,
        opportunity_id: str,
        match_score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log when a user views a recommendation.
        
        This tracks recommendation impressions for analytics and helps
        measure recommendation relevance and engagement rates.
        
        Args:
            user_id: User identifier
            opportunity_id: Opportunity being viewed
            match_score: The match score for this recommendation
            context: Optional additional context (e.g., search query, filter settings)
        
        Returns:
            Event record dict with timestamp and IDs
        """
        # Get active experiment variants for this user
        experiment_info = self._get_user_experiments(user_id)
        
        # Create UserEvent record for each active experiment
        event_records = []
        for exp in experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_VIEWED,
                opportunity_id=opportunity_id,
                experiment_name=exp["experiment_name"],
                variant_name=exp["variant_name"],
                match_score=match_score,
                event_metadata=context or {},
                session_id=context.get("session_id") if context else None,
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
        
        # If no active experiments, still track the event
        if not experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_VIEWED,
                opportunity_id=opportunity_id,
                match_score=match_score,
                event_metadata=context or {},
                session_id=context.get("session_id") if context else None,
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
        
        self.db.commit()
        
        return {
            "event_type": EventType.RECOMMENDATION_VIEWED,
            "event_count": len(event_records),
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "match_score": match_score,
            "experiments": experiment_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def log_recommendation_saved(
        self,
        user_id: str,
        opportunity_id: str,
        source: str = "dashboard"
    ) -> Dict[str, Any]:
        """
        Log when a user saves/bookmarks a recommendation.
        
        This indicates high interest and is a key engagement metric.
        
        Args:
            user_id: User identifier
            opportunity_id: Opportunity being saved
            source: Where the save action originated (dashboard, search, etc.)
        
        Returns:
            Event record dict
        """
        # Get active experiments
        experiment_info = self._get_user_experiments(user_id)
        
        # Update or create application record with saved=True
        application = self.db.query(Application).filter(
            and_(
                Application.user_id == user_id,
                Application.opportunity_id == opportunity_id
            )
        ).first()
        
        if application:
            application.saved = True
            application.updated_at = datetime.utcnow()
        else:
            # Create new application record in DISCOVERED state
            application = Application(
                user_id=user_id,
                opportunity_id=opportunity_id,
                saved=True,
                state="discovered"
            )
            self.db.add(application)
        
        self.db.flush()  # Ensure application.id is available
        
        # Create UserEvent records
        event_records = []
        for exp in experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_SAVED,
                opportunity_id=opportunity_id,
                application_id=application.id,
                experiment_name=exp["experiment_name"],
                variant_name=exp["variant_name"],
                event_metadata={"source": source},
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
        
        # If no active experiments, still track the event
        if not experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_SAVED,
                opportunity_id=opportunity_id,
                application_id=application.id,
                event_metadata={"source": source},
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
        
        self.db.commit()
        
        return {
            "event_type": EventType.RECOMMENDATION_SAVED,
            "event_count": len(event_records),
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "application_id": application.id,
            "source": source,
            "experiments": experiment_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def log_recommendation_applied(
        self,
        user_id: str,
        opportunity_id: str,
        application_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log when a user applies to a recommendation.
        
        This is the primary conversion event for measuring recommendation
        effectiveness and A/B test performance.
        
        Args:
            user_id: User identifier
            opportunity_id: Opportunity being applied to
            application_id: Optional existing application ID
        
        Returns:
            Event record dict
        """
        # Get active experiments
        experiment_info = self._get_user_experiments(user_id)
        
        # Create UserEvent records
        event_records = []
        for exp in experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_APPLIED,
                opportunity_id=opportunity_id,
                application_id=application_id,
                experiment_name=exp["experiment_name"],
                variant_name=exp["variant_name"],
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
            
            # Also create feedback record for experiment tracking
            feedback = Feedback(
                user_id=user_id,
                opportunity_id=opportunity_id,
                feedback_type="applied",
                experiment_name=exp["experiment_name"],
                variant_name=exp["variant_name"],
                created_at=datetime.utcnow()
            )
            self.db.add(feedback)
        
        # If no active experiments, still track the event
        if not experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_APPLIED,
                opportunity_id=opportunity_id,
                application_id=application_id,
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
        
        self.db.commit()
        
        return {
            "event_type": EventType.RECOMMENDATION_APPLIED,
            "event_count": len(event_records),
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "application_id": application_id,
            "experiments": experiment_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def log_recommendation_dismissed(
        self,
        user_id: str,
        opportunity_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log when a user dismisses/ignores a recommendation.
        
        This helps identify false positives and improve recommendation quality.
        
        Args:
            user_id: User identifier
            opportunity_id: Opportunity being dismissed
            reason: Optional reason (not_interested, not_eligible, etc.)
        
        Returns:
            Event record dict
        """
        # Get active experiments
        experiment_info = self._get_user_experiments(user_id)
        
        # Create UserEvent records
        event_records = []
        for exp in experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_DISMISSED,
                opportunity_id=opportunity_id,
                experiment_name=exp["experiment_name"],
                variant_name=exp["variant_name"],
                event_metadata={"reason": reason} if reason else {},
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
            
            # Also create feedback record for experiment tracking
            feedback = Feedback(
                user_id=user_id,
                opportunity_id=opportunity_id,
                feedback_type=reason or "ignored",
                experiment_name=exp["experiment_name"],
                variant_name=exp["variant_name"],
                created_at=datetime.utcnow()
            )
            self.db.add(feedback)
        
        # If no active experiments, still track the event
        if not experiment_info:
            event = UserEvent(
                user_id=user_id,
                event_type=EventType.RECOMMENDATION_DISMISSED,
                opportunity_id=opportunity_id,
                event_metadata={"reason": reason} if reason else {},
                created_at=datetime.utcnow()
            )
            self.db.add(event)
            event_records.append(event)
        
        self.db.commit()
        
        return {
            "event_type": EventType.RECOMMENDATION_DISMISSED,
            "event_count": len(event_records),
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "reason": reason,
            "experiments": experiment_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def collect_feedback(
        self,
        user_id: str,
        opportunity_id: str,
        feedback_type: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect explicit user feedback on recommendations.
        
        Supports feedback types: relevant, not_relevant, ineligible, applied, ignored
        
        Args:
            user_id: User identifier
            opportunity_id: Opportunity being rated
            feedback_type: Type of feedback (relevant, not_relevant, etc.)
            comment: Optional text comment
        
        Returns:
            Created feedback record
        
        **Validates: Requirements 21.1, 21.2**
        """
        # Get active experiments for this user
        experiment_info = self._get_user_experiments(user_id)
        
        # Create feedback record with experiment tracking
        feedback_records = []
        for exp in experiment_info:
            feedback = Feedback(
                user_id=user_id,
                opportunity_id=opportunity_id,
                feedback_type=feedback_type,
                comment=comment,
                experiment_name=exp["experiment_name"],
                variant_name=exp["variant_name"],
                created_at=datetime.utcnow()
            )
            self.db.add(feedback)
            feedback_records.append(feedback)
        
        # If no active experiments, still create feedback without experiment tracking
        if not experiment_info:
            feedback = Feedback(
                user_id=user_id,
                opportunity_id=opportunity_id,
                feedback_type=feedback_type,
                comment=comment,
                created_at=datetime.utcnow()
            )
            self.db.add(feedback)
            feedback_records.append(feedback)
        
        self.db.commit()
        
        return {
            "feedback_count": len(feedback_records),
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "feedback_type": feedback_type,
            "experiments": experiment_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_user_activity_summary(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary of user activity within a date range.
        
        Args:
            user_id: User identifier
            start_date: Optional start date for activity window
            end_date: Optional end date for activity window
        
        Returns:
            Dict with activity counts by type
        """
        # Build date filter
        date_filter = []
        if start_date:
            date_filter.append(Feedback.created_at >= start_date)
        if end_date:
            date_filter.append(Feedback.created_at <= end_date)
        
        # Get feedback counts by type
        feedback_summary = self.db.query(
            Feedback.feedback_type,
            func.count(Feedback.id)
        ).filter(
            Feedback.user_id == user_id,
            *date_filter
        ).group_by(Feedback.feedback_type).all()
        
        # Get application counts by state
        application_summary = self.db.query(
            Application.state,
            func.count(Application.id)
        ).filter(
            Application.user_id == user_id,
            *date_filter if date_filter else []
        ).group_by(Application.state).all()
        
        return {
            "user_id": user_id,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "feedback": {
                feedback_type: count 
                for feedback_type, count in feedback_summary
            },
            "applications": {
                str(state): count 
                for state, count in application_summary
            }
        }
    
    def get_opportunity_engagement_metrics(
        self,
        opportunity_id: str
    ) -> Dict[str, Any]:
        """
        Get engagement metrics for a specific opportunity.
        
        Args:
            opportunity_id: Opportunity identifier
        
        Returns:
            Dict with engagement metrics (views, saves, applications, feedback)
        """
        # Get application stats
        total_applications = self.db.query(func.count(Application.id)).filter(
            Application.opportunity_id == opportunity_id
        ).scalar()
        
        saved_count = self.db.query(func.count(Application.id)).filter(
            and_(
                Application.opportunity_id == opportunity_id,
                Application.saved == True
            )
        ).scalar()
        
        # Get feedback stats
        feedback_counts = self.db.query(
            Feedback.feedback_type,
            func.count(Feedback.id)
        ).filter(
            Feedback.opportunity_id == opportunity_id
        ).group_by(Feedback.feedback_type).all()
        
        feedback_summary = {
            feedback_type: count 
            for feedback_type, count in feedback_counts
        }
        
        # Calculate engagement rate
        total_interactions = sum(feedback_summary.values()) + saved_count
        applied_count = feedback_summary.get("applied", 0)
        engagement_rate = applied_count / total_interactions if total_interactions > 0 else 0.0
        
        return {
            "opportunity_id": opportunity_id,
            "total_applications": total_applications or 0,
            "saved_count": saved_count or 0,
            "feedback": feedback_summary,
            "total_interactions": total_interactions,
            "engagement_rate": round(engagement_rate, 4)
        }
    
    def _get_user_experiments(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get active experiment assignments for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of dicts with experiment_name and variant_name
        """
        assignments = self.db.query(UserExperiment).filter(
            UserExperiment.user_id == user_id
        ).all()
        
        return [
            {
                "experiment_name": a.experiment_name,
                "variant_name": a.variant_name
            }
            for a in assignments
        ]
    
    def track_experiment_event(
        self,
        user_id: str,
        experiment_name: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a custom event within an experiment context.
        
        This is a flexible method for tracking any experiment-related event
        beyond the standard recommendation events.
        
        Args:
            user_id: User identifier
            experiment_name: Name of the experiment
            event_type: Type of event being tracked
            metadata: Optional event metadata
        
        Returns:
            Event record dict
        
        **Validates: Requirements 20.1, 20.3**
        """
        # Get user's variant for this experiment
        assignment = self.db.query(UserExperiment).filter(
            and_(
                UserExperiment.user_id == user_id,
                UserExperiment.experiment_name == experiment_name
            )
        ).first()
        
        if not assignment:
            return {
                "error": f"User {user_id} not assigned to experiment {experiment_name}"
            }
        
        return {
            "event_type": event_type,
            "user_id": user_id,
            "experiment_name": experiment_name,
            "variant_name": assignment.variant_name,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
