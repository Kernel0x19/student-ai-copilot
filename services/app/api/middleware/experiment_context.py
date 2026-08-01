"""Middleware for tracking experiment variant assignments in request context

This middleware automatically assigns users to experiments and adds variant
information to the request state for use throughout the request lifecycle.

**Requirements**: 20.3 - Track variant assignment in user session metadata
"""

from contextvars import ContextVar
from typing import Dict, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.analytics.experiment_service import ExperimentService
from app.db.session import SessionLocal

# Context variable to store experiment assignments for the current request
_experiment_context: ContextVar[Dict[str, str]] = ContextVar(
    "experiment_context", default={}
)


class ExperimentContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically assign users to experiments and track variants.
    
    This middleware:
    1. Extracts user_id from request (if authenticated)
    2. Assigns user to active experiments (if not already assigned)
    3. Stores variant assignments in request.state for access in endpoints
    4. Adds experiment context to request context variable
    
    Usage:
        app.add_middleware(ExperimentContextMiddleware)
        
        # In route handlers:
        variant = request.state.experiments.get("recommendation_algorithm")
    """
    
    async def dispatch(self, request: Request, call_next):
        # Initialize experiment context
        experiment_assignments = {}
        
        # Try to get user_id from request
        user_id = None
        
        # Check if user is authenticated (user object should be set by auth middleware)
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
        
        # If we have a user, assign them to active experiments
        if user_id:
            db = SessionLocal()
            try:
                service = ExperimentService(db)
                active_experiments = service.get_all_active_experiments()
                
                # Assign user to each active experiment
                for experiment_name in active_experiments:
                    try:
                        variant = service.assign_user_to_variant(user_id, experiment_name)
                        experiment_assignments[experiment_name] = variant
                    except Exception:
                        # If assignment fails, continue with other experiments
                        pass
                
            finally:
                db.close()
        
        # Store assignments in request state
        request.state.experiments = experiment_assignments
        
        # Set context variable
        token = _experiment_context.set(experiment_assignments)
        
        try:
            response = await call_next(request)
            
            # Optionally add experiment info to response headers for debugging
            if experiment_assignments:
                response.headers["X-Experiments"] = ",".join(
                    f"{exp}:{var}" for exp, var in experiment_assignments.items()
                )
            
            return response
        finally:
            # Reset context variable
            _experiment_context.reset(token)


def get_experiment_context() -> Dict[str, str]:
    """
    Get the current experiment context from the context variable.
    
    Returns:
        Dict mapping experiment names to assigned variant names
        
    Usage:
        from app.api.middleware.experiment_context import get_experiment_context
        
        context = get_experiment_context()
        variant = context.get("recommendation_algorithm", "control")
    """
    return _experiment_context.get()


def get_variant_for_experiment(experiment_name: str) -> Optional[str]:
    """
    Get the variant assigned for a specific experiment in the current context.
    
    Args:
        experiment_name: Name of the experiment
        
    Returns:
        Variant name if assigned, None otherwise
        
    Usage:
        from app.api.middleware.experiment_context import get_variant_for_experiment
        
        variant = get_variant_for_experiment("recommendation_algorithm")
        if variant == "treatment_ml":
            # Use ML-enhanced algorithm
            pass
        else:
            # Use control/baseline algorithm
            pass
    """
    context = get_experiment_context()
    return context.get(experiment_name)

