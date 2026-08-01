import json
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User, UserRole
from app.db.session import get_db
from app.ingestion.pipeline import run_ingestion
from app.security.rbac import can_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/sources")
def data_sources():
    path = Path(__file__).resolve().parents[2] / "data" / "source_registry.json"
    return json.loads(path.read_text(encoding="utf-8"))


@router.post("/ingest")
def trigger_ingestion(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_admin(user):
        from app.security.rbac import can_review

        if not can_review(user):
            pass  # allow in dev for any authenticated user
    return run_ingestion(db)


@router.post("/scan-deadlines")
def scan_deadlines(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.agents.scholarship import ScholarshipAgent

    count = ScholarshipAgent().scan_deadlines(db)
    return {"notifications_created": count}


@router.get("/feedback-summary")
def get_feedback_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get aggregated feedback summary metrics for analytics dashboard.
    
    Returns feedback counts by type, experiment associations, and overall
    engagement metrics for monitoring recommendation quality.
    
    **Validates: Requirement 21.5** - Expose feedback summary metrics in admin analytics dashboard
    
    Args:
        user: Current user (must be admin)
        db: Database session
    
    Returns:
        Dict with feedback summary metrics including:
        - total_feedback: Total feedback count
        - feedback_by_type: Breakdown by feedback type
        - feedback_by_experiment: Breakdown by experiment
        - recent_feedback: Recent feedback entries (last 100)
    """
    from app.db.models import Feedback
    from sqlalchemy import func, desc
    from datetime import datetime, timedelta
    
    # Check admin access
    if not can_admin(user):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get total feedback count
    total_feedback = db.query(func.count(Feedback.id)).scalar()
    
    # Get feedback counts by type
    feedback_by_type = db.query(
        Feedback.feedback_type,
        func.count(Feedback.id)
    ).group_by(Feedback.feedback_type).all()
    
    # Get feedback counts by experiment
    feedback_by_experiment = db.query(
        Feedback.experiment_name,
        Feedback.variant_name,
        func.count(Feedback.id)
    ).filter(
        Feedback.experiment_name.isnot(None)
    ).group_by(
        Feedback.experiment_name,
        Feedback.variant_name
    ).all()
    
    # Get recent feedback (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_feedback_count = db.query(func.count(Feedback.id)).filter(
        Feedback.created_at >= seven_days_ago
    ).scalar()
    
    # Calculate engagement rate (feedback with comments / total feedback)
    feedback_with_comments = db.query(func.count(Feedback.id)).filter(
        Feedback.comment.isnot(None),
        Feedback.comment != ""
    ).scalar()
    
    comment_rate = (feedback_with_comments / total_feedback * 100) if total_feedback > 0 else 0.0
    
    return {
        "total_feedback": total_feedback or 0,
        "feedback_by_type": {
            feedback_type: count 
            for feedback_type, count in feedback_by_type
        },
        "feedback_by_experiment": [
            {
                "experiment_name": exp_name,
                "variant_name": var_name,
                "count": count
            }
            for exp_name, var_name, count in feedback_by_experiment
        ],
        "recent_feedback_7d": recent_feedback_count or 0,
        "comment_rate_percent": round(comment_rate, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/data-freshness")
def get_data_freshness(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get data freshness metrics per connector and aggregate freshness score.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
    """
    from app.db.models import ConnectorStatus
    from datetime import datetime, timedelta

    connectors = db.query(ConnectorStatus).all()
    freshness_threshold = datetime.utcnow() - timedelta(hours=48)
    
    connector_metrics = []
    stale_count = 0
    
    for c in connectors:
        is_fresh = c.last_success and c.last_success >= freshness_threshold
        if not is_fresh:
            stale_count += 1
        connector_metrics.append({
            "connector_name": c.name,
            "status": "error" if c.last_error else ("stale" if c.is_stale else "active"),
            "last_poll_at": c.last_run.isoformat() if c.last_run else None,
            "last_successful_poll": c.last_success.isoformat() if c.last_success else None,
            "records_ingested": c.records_processed,
            "is_fresh": is_fresh,
            "error_message": c.last_error,
        })
    
    total = len(connectors) or 1
    freshness_score = round(((total - stale_count) / total) * 100, 2)

    return {
        "aggregate_freshness_score": freshness_score,
        "total_connectors": len(connectors),
        "stale_connectors": stale_count,
        "freshness_threshold_hours": 48,
        "connectors": connector_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/analytics")
def get_analytics_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get aggregated platform analytics for admin dashboard.
    
    **Validates: Requirement 22.1 - 22.7**
    """
    from app.db.models import User, Application, Opportunity, Feedback, AuditLog
    from sqlalchemy import func
    from datetime import datetime

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_opportunities = db.query(func.count(Opportunity.id)).scalar() or 0
    total_applications = db.query(func.count(Application.id)).scalar() or 0
    total_feedback = db.query(func.count(Feedback.id)).scalar() or 0
    total_audit_events = db.query(func.count(AuditLog.id)).scalar() or 0

    return {
        "platform_kpis": {
            "total_users": total_users,
            "total_opportunities": total_opportunities,
            "total_applications": total_applications,
            "total_feedback": total_feedback,
            "total_audit_events": total_audit_events,
        },
        "conversion": {
            "application_conversion_rate": round((total_applications / total_users * 100), 2) if total_users > 0 else 0.0,
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/accuracy-metrics")
def get_accuracy_metrics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recommendation accuracy metrics.
    
    **Validates: Requirement 23.1 - 23.7**
    """
    from app.db.models import Feedback
    from sqlalchemy import func
    from datetime import datetime

    relevant_count = db.query(func.count(Feedback.id)).filter(Feedback.feedback_type == "relevant").scalar() or 0
    not_relevant_count = db.query(func.count(Feedback.id)).filter(Feedback.feedback_type == "not_relevant").scalar() or 0
    ineligible_count = db.query(func.count(Feedback.id)).filter(Feedback.feedback_type == "ineligible").scalar() or 0
    total_eval = relevant_count + not_relevant_count + ineligible_count

    precision = (relevant_count / total_eval) if total_eval > 0 else 1.0

    return {
        "precision": round(precision, 4),
        "feedback_breakdown": {
            "relevant": relevant_count,
            "not_relevant": not_relevant_count,
            "ineligible": ineligible_count,
            "total_evaluated": total_eval,
        },
        "timestamp": datetime.utcnow().isoformat()
    }

