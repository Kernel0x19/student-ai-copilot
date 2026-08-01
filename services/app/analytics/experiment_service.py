"""A/B Testing Experiment Service

This module provides the core functionality for managing A/B experiments,
including experiment creation, user assignment, and variant tracking.
"""

import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import ExperimentVariant, UserExperiment


class ExperimentService:
    """Service for managing A/B testing experiments"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_experiment(
        self,
        experiment_name: str,
        variants: List[Dict[str, Any]]
    ) -> List[ExperimentVariant]:
        """
        Create a new A/B experiment with control and treatment variants.
        
        Args:
            experiment_name: Unique name for the experiment
            variants: List of variant configurations, e.g.:
                [
                    {"name": "control", "config": {"algorithm": "baseline"}},
                    {"name": "treatment_a", "config": {"algorithm": "ml_enhanced"}}
                ]
        
        Returns:
            List of created ExperimentVariant objects
        
        Raises:
            ValueError: If experiment with this name already exists
        """
        # Check if experiment already exists
        existing = self.db.query(ExperimentVariant).filter(
            ExperimentVariant.experiment_name == experiment_name
        ).first()
        
        if existing:
            raise ValueError(f"Experiment '{experiment_name}' already exists")
        
        # Create variant records
        created_variants = []
        for variant_spec in variants:
            variant = ExperimentVariant(
                experiment_name=experiment_name,
                variant_name=variant_spec["name"],
                is_active=True,
                config=variant_spec.get("config", {})
            )
            self.db.add(variant)
            created_variants.append(variant)
        
        self.db.commit()
        return created_variants
    
    def get_experiment_variants(self, experiment_name: str) -> List[ExperimentVariant]:
        """
        Get all variants for an experiment.
        
        Args:
            experiment_name: Name of the experiment
        
        Returns:
            List of ExperimentVariant objects
        """
        return self.db.query(ExperimentVariant).filter(
            and_(
                ExperimentVariant.experiment_name == experiment_name,
                ExperimentVariant.is_active == True
            )
        ).all()
    
    def assign_user_to_variant(
        self,
        user_id: str,
        experiment_name: str
    ) -> str:
        """
        Deterministically assign a user to an experiment variant using user_id hash.
        
        This method uses consistent hashing to ensure:
        - The same user always gets the same variant
        - Users are evenly distributed across variants
        - Assignment is deterministic and reproducible
        
        Args:
            user_id: User identifier
            experiment_name: Name of the experiment
        
        Returns:
            Variant name the user is assigned to
        
        Raises:
            ValueError: If experiment doesn't exist or has no active variants
        """
        # Check if user already assigned
        existing = self.db.query(UserExperiment).filter(
            and_(
                UserExperiment.user_id == user_id,
                UserExperiment.experiment_name == experiment_name
            )
        ).first()
        
        if existing:
            return existing.variant_name
        
        # Get active variants
        variants = self.get_experiment_variants(experiment_name)
        
        if not variants:
            raise ValueError(f"No active variants found for experiment '{experiment_name}'")
        
        # Deterministic assignment using hash
        variant_name = self._hash_user_to_variant(user_id, experiment_name, variants)
        
        # Record assignment
        assignment = UserExperiment(
            user_id=user_id,
            experiment_name=experiment_name,
            variant_name=variant_name,
            assigned_at=datetime.utcnow()
        )
        self.db.add(assignment)
        self.db.commit()
        
        return variant_name
    
    def _hash_user_to_variant(
        self,
        user_id: str,
        experiment_name: str,
        variants: List[ExperimentVariant]
    ) -> str:
        """
        Use consistent hashing to deterministically assign user to variant.
        
        Args:
            user_id: User identifier
            experiment_name: Experiment name (for namespace isolation)
            variants: List of available variants
        
        Returns:
            Selected variant name
        """
        # Create hash input combining user_id and experiment_name
        # This ensures different experiments give different assignments
        hash_input = f"{user_id}:{experiment_name}"
        
        # Use SHA-256 for good distribution
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Convert first 8 hex chars to integer
        hash_int = int(hash_digest[:8], 16)
        
        # Map to variant index using modulo
        variant_index = hash_int % len(variants)
        
        return variants[variant_index].variant_name
    
    def get_user_variant(
        self,
        user_id: str,
        experiment_name: str
    ) -> Optional[str]:
        """
        Get the variant assigned to a user for a specific experiment.
        
        Args:
            user_id: User identifier
            experiment_name: Name of the experiment
        
        Returns:
            Variant name if assigned, None otherwise
        """
        assignment = self.db.query(UserExperiment).filter(
            and_(
                UserExperiment.user_id == user_id,
                UserExperiment.experiment_name == experiment_name
            )
        ).first()
        
        return assignment.variant_name if assignment else None
    
    def get_variant_config(
        self,
        experiment_name: str,
        variant_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific variant.
        
        Args:
            experiment_name: Name of the experiment
            variant_name: Name of the variant
        
        Returns:
            Variant configuration dict, or None if not found
        """
        variant = self.db.query(ExperimentVariant).filter(
            and_(
                ExperimentVariant.experiment_name == experiment_name,
                ExperimentVariant.variant_name == variant_name,
                ExperimentVariant.is_active == True
            )
        ).first()
        
        return variant.config if variant else None
    
    def deactivate_experiment(self, experiment_name: str) -> int:
        """
        Deactivate all variants of an experiment.
        
        Args:
            experiment_name: Name of the experiment to deactivate
        
        Returns:
            Number of variants deactivated
        """
        count = self.db.query(ExperimentVariant).filter(
            ExperimentVariant.experiment_name == experiment_name
        ).update({"is_active": False})
        
        self.db.commit()
        return count
    
    def promote_variant_to_default(
        self,
        experiment_name: str,
        winning_variant: str
    ) -> Dict[str, Any]:
        """
        Graduate an experiment by promoting a winning variant to default.
        
        This deactivates the experiment and returns the winning variant's
        configuration for promotion to the default behavior.
        
        Args:
            experiment_name: Name of the experiment
            winning_variant: Name of the variant to promote
        
        Returns:
            Configuration dict of the winning variant
        
        Raises:
            ValueError: If experiment or variant not found
        """
        # Get winning variant config
        config = self.get_variant_config(experiment_name, winning_variant)
        
        if config is None:
            raise ValueError(
                f"Variant '{winning_variant}' not found in experiment '{experiment_name}'"
            )
        
        # Deactivate experiment
        self.deactivate_experiment(experiment_name)
        
        return config
    
    def get_all_active_experiments(self) -> List[str]:
        """
        Get names of all active experiments.
        
        Returns:
            List of experiment names
        """
        results = self.db.query(ExperimentVariant.experiment_name).filter(
            ExperimentVariant.is_active == True
        ).distinct().all()
        
        return [r[0] for r in results]
    
    def get_user_experiments(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all experiment assignments for a user.
        
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
                "variant_name": a.variant_name,
                "assigned_at": a.assigned_at.isoformat()
            }
            for a in assignments
        ]
