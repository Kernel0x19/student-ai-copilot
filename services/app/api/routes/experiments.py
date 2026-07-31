"""API endpoints for A/B testing experiments"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics.experiment_service import ExperimentService
from app.analytics.metrics_calculator import MetricsCalculator
from app.api.deps import get_current_user, get_db
from app.db.models import User, UserRole
from app.schemas.experiments import (
    ExperimentComparisonResponse,
    ExperimentCreate,
    ExperimentMetricsResponse,
    ExperimentSummary,
    ExperimentVariantResponse,
    PromoteVariantRequest,
    PromoteVariantResponse,
    UserAssignmentResponse,
)
from app.security.rbac import can_admin

router = APIRouter(prefix="/experiments", tags=["experiments"])


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    if not can_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/", response_model=List[ExperimentVariantResponse], status_code=201)
def create_experiment(
    experiment: ExperimentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Create a new A/B testing experiment with control and treatment variants.
    
    Requires admin role.
    
    **Requirements**: 20.1 - Support defining experiments with control/treatment variants
    """
    service = ExperimentService(db)
    
    try:
        variants = service.create_experiment(
            experiment_name=experiment.experiment_name,
            variants=[v.model_dump() for v in experiment.variants]
        )
        return variants
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[str])
def list_active_experiments(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Get list of all active experiments.
    
    Requires admin role.
    """
    service = ExperimentService(db)
    return service.get_all_active_experiments()


@router.get("/summary", response_model=List[ExperimentSummary])
def get_all_experiments_summary(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Get summary statistics for all experiments.
    
    Requires admin role.
    """
    calculator = MetricsCalculator(db)
    return calculator.get_all_experiments_summary()


@router.get("/{experiment_name}", response_model=List[ExperimentVariantResponse])
def get_experiment_variants(
    experiment_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Get all variants for a specific experiment.
    
    Requires admin role.
    """
    service = ExperimentService(db)
    variants = service.get_experiment_variants(experiment_name)
    
    if not variants:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_name}' not found")
    
    return variants


@router.get("/{experiment_name}/summary", response_model=ExperimentSummary)
def get_experiment_summary(
    experiment_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Get high-level summary for a specific experiment.
    
    Requires admin role.
    """
    calculator = MetricsCalculator(db)
    return calculator.get_experiment_summary(experiment_name)


@router.post("/{experiment_name}/assign/{user_id}", response_model=UserAssignmentResponse)
def assign_user_to_experiment(
    experiment_name: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign a user to an experiment variant using deterministic hashing.
    
    This endpoint uses consistent hashing based on user_id to ensure:
    - Same user always gets the same variant
    - Even distribution across variants
    - Reproducible assignments
    
    **Requirements**: 20.2 - Deterministic user assignment using user_id hash
    """
    # Users can only assign themselves, admins can assign anyone
    if not can_admin(current_user) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot assign other users")
    
    service = ExperimentService(db)
    
    try:
        variant_name = service.assign_user_to_variant(user_id, experiment_name)
        
        # Get assignment details
        from app.db.models import UserExperiment
        assignment = db.query(UserExperiment).filter(
            UserExperiment.user_id == user_id,
            UserExperiment.experiment_name == experiment_name
        ).first()
        
        return UserAssignmentResponse(
            user_id=assignment.user_id,
            experiment_name=assignment.experiment_name,
            variant_name=assignment.variant_name,
            assigned_at=assignment.assigned_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{experiment_name}/user/{user_id}/variant")
def get_user_variant(
    experiment_name: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the variant assigned to a user for a specific experiment.
    
    Returns None if user is not yet assigned to this experiment.
    
    **Requirements**: 20.3 - Track variant assignment in user session metadata
    """
    # Users can only check themselves, admins can check anyone
    if not can_admin(current_user) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other user's assignments")
    
    service = ExperimentService(db)
    variant = service.get_user_variant(user_id, experiment_name)
    
    return {
        "experiment_name": experiment_name,
        "user_id": user_id,
        "variant_name": variant
    }


@router.get("/{experiment_name}/metrics", response_model=ExperimentMetricsResponse)
def get_experiment_metrics(
    experiment_name: str,
    start_date: Optional[datetime] = Query(None, description="Start date for metrics (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics (ISO format)"),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Calculate comprehensive metrics for an experiment including conversion rate and engagement.
    
    Metrics include:
    - Conversion rate (applications per user)
    - Engagement rate (users who provided feedback)
    - Application rate (applications per interaction)
    - Relevance score (positive feedback ratio)
    
    Requires admin role.
    
    **Requirements**: 20.6 - Calculate experiment metrics (conversion rate, engagement, application completion)
    """
    calculator = MetricsCalculator(db)
    metrics = calculator.calculate_experiment_metrics(experiment_name, start_date, end_date)
    
    if not metrics.get("variants"):
        raise HTTPException(status_code=404, detail=f"No data found for experiment '{experiment_name}'")
    
    return metrics


@router.get("/{experiment_name}/compare", response_model=ExperimentComparisonResponse)
def compare_variants(
    experiment_name: str,
    control_variant: str = Query("control", description="Name of the control variant"),
    start_date: Optional[datetime] = Query(None, description="Start date for comparison (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date for comparison (ISO format)"),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Compare treatment variants against control variant with lift calculations.
    
    Returns percentage lift for each key metric compared to control.
    
    Requires admin role.
    
    **Requirements**: 20.6 - Calculate and expose experiment metrics per variant
    """
    calculator = MetricsCalculator(db)
    comparison = calculator.compare_variants(experiment_name, control_variant, start_date, end_date)
    
    if "error" in comparison:
        raise HTTPException(status_code=404, detail=comparison["error"])
    
    return comparison


@router.post("/{experiment_name}/promote", response_model=PromoteVariantResponse)
def promote_variant(
    experiment_name: str,
    request: PromoteVariantRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Graduate an experiment by promoting a winning variant to default.
    
    This deactivates the experiment and returns the winning variant's configuration
    for promotion to the default system behavior.
    
    Requires admin role.
    
    **Requirements**: 20.7 - Support experiment graduation (promoting treatment to default)
    """
    service = ExperimentService(db)
    
    try:
        config = service.promote_variant_to_default(experiment_name, request.winning_variant)
        
        return PromoteVariantResponse(
            experiment_name=experiment_name,
            winning_variant=request.winning_variant,
            config=config,
            message=f"Experiment '{experiment_name}' graduated. Variant '{request.winning_variant}' promoted to default."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{experiment_name}", status_code=200)
def deactivate_experiment(
    experiment_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    Deactivate an experiment and all its variants.
    
    Requires admin role.
    """
    service = ExperimentService(db)
    count = service.deactivate_experiment(experiment_name)
    
    if count == 0:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_name}' not found")
    
    return {
        "experiment_name": experiment_name,
        "variants_deactivated": count,
        "message": f"Experiment '{experiment_name}' deactivated successfully"
    }


@router.get("/user/{user_id}/assignments", response_model=List[UserAssignmentResponse])
def get_user_assignments(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all experiment assignments for a user.
    
    Users can only view their own assignments unless they are an admin.
    """
    # Users can only check themselves, admins can check anyone
    if not can_admin(current_user) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other user's assignments")
    
    service = ExperimentService(db)
    assignments = service.get_user_experiments(user_id)
    
    return [
        UserAssignmentResponse(
            user_id=user_id,
            experiment_name=a["experiment_name"],
            variant_name=a["variant_name"],
            assigned_at=datetime.fromisoformat(a["assigned_at"])
        )
        for a in assignments
    ]

