"""Experiment Metrics Calculator

This module calculates key metrics for A/B testing experiments including:
- Conversion rates (applications per recommendation)
- Engagement rates (user interactions)
- Application completion rates
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case

from app.db.models import UserExperiment, Feedback, AccuracyMetric


class MetricsCalculator:
    """Calculate experiment performance metrics"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def calculate_experiment_metrics(
        self,
        experiment_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics for an experiment.
        
        Args:
            experiment_name: Name of the experiment
            start_date: Optional start date for metric calculation
            end_date: Optional end date for metric calculation
        
        Returns:
            Dict containing metrics per variant:
            {
                "experiment_name": str,
                "period": {"start": str, "end": str},
                "variants": {
                    "control": {
                        "users": int,
                        "conversion_rate": float,
                        "engagement_rate": float,
                        "application_rate": float,
                        "relevance_score": float
                    },
                    "treatment_a": {...}
                }
            }
        """
        # Set default date range if not provided
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        # Get all variants for this experiment
        variants = self.db.query(UserExperiment.variant_name).filter(
            and_(
                UserExperiment.experiment_name == experiment_name,
                UserExperiment.assigned_at >= start_date,
                UserExperiment.assigned_at <= end_date
            )
        ).distinct().all()
        
        variant_names = [v[0] for v in variants]
        
        # Calculate metrics for each variant
        variant_metrics = {}
        for variant_name in variant_names:
            variant_metrics[variant_name] = self._calculate_variant_metrics(
                experiment_name,
                variant_name,
                start_date,
                end_date
            )
        
        return {
            "experiment_name": experiment_name,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "variants": variant_metrics
        }
    
    def _calculate_variant_metrics(
        self,
        experiment_name: str,
        variant_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate metrics for a specific variant"""
        
        # Get users in this variant
        user_assignments = self.db.query(UserExperiment).filter(
            and_(
                UserExperiment.experiment_name == experiment_name,
                UserExperiment.variant_name == variant_name,
                UserExperiment.assigned_at >= start_date,
                UserExperiment.assigned_at <= end_date
            )
        ).all()
        
        user_ids = [a.user_id for a in user_assignments]
        total_users = len(user_ids)
        
        if total_users == 0:
            return self._empty_metrics()
        
        # Get feedback for these users
        feedback_records = self.db.query(Feedback).filter(
            and_(
                Feedback.user_id.in_(user_ids),
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date,
                Feedback.experiment_name == experiment_name,
                Feedback.variant_name == variant_name
            )
        ).all()
        
        # Calculate metrics
        total_feedback = len(feedback_records)
        applied_count = sum(1 for f in feedback_records if f.feedback_type == 'applied')
        relevant_count = sum(1 for f in feedback_records if f.feedback_type == 'relevant')
        engaged_count = sum(
            1 for f in feedback_records 
            if f.feedback_type in ['applied', 'relevant', 'not_relevant', 'ineligible']
        )
        
        # Engagement rate: users who provided any feedback
        users_with_feedback = len(set(f.user_id for f in feedback_records))
        engagement_rate = users_with_feedback / total_users if total_users > 0 else 0.0
        
        # Conversion rate: applications per user
        conversion_rate = applied_count / total_users if total_users > 0 else 0.0
        
        # Application rate: applied / total feedback interactions
        application_rate = applied_count / total_feedback if total_feedback > 0 else 0.0
        
        # Relevance score: relevant + applied / total feedback
        positive_feedback = relevant_count + applied_count
        relevance_score = positive_feedback / total_feedback if total_feedback > 0 else 0.0
        
        return {
            "users": total_users,
            "total_interactions": total_feedback,
            "conversion_rate": round(conversion_rate, 4),
            "engagement_rate": round(engagement_rate, 4),
            "application_rate": round(application_rate, 4),
            "relevance_score": round(relevance_score, 4),
            "breakdown": {
                "applied": applied_count,
                "relevant": relevant_count,
                "not_relevant": sum(1 for f in feedback_records if f.feedback_type == 'not_relevant'),
                "ineligible": sum(1 for f in feedback_records if f.feedback_type == 'ineligible'),
                "ignored": sum(1 for f in feedback_records if f.feedback_type == 'ignored')
            }
        }
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            "users": 0,
            "total_interactions": 0,
            "conversion_rate": 0.0,
            "engagement_rate": 0.0,
            "application_rate": 0.0,
            "relevance_score": 0.0,
            "breakdown": {
                "applied": 0,
                "relevant": 0,
                "not_relevant": 0,
                "ineligible": 0,
                "ignored": 0
            }
        }
    
    def compare_variants(
        self,
        experiment_name: str,
        control_variant: str = "control",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Compare treatment variants against control variant.
        
        Args:
            experiment_name: Name of the experiment
            control_variant: Name of the control variant (default: "control")
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Dict with comparison results including lifts and statistical significance
        """
        metrics = self.calculate_experiment_metrics(experiment_name, start_date, end_date)
        
        if control_variant not in metrics["variants"]:
            return {
                "error": f"Control variant '{control_variant}' not found in experiment"
            }
        
        control_metrics = metrics["variants"][control_variant]
        comparisons = {}
        
        for variant_name, variant_metrics in metrics["variants"].items():
            if variant_name == control_variant:
                continue
            
            comparison = {
                "variant": variant_name,
                "lifts": {}
            }
            
            # Calculate lifts for key metrics
            for metric in ["conversion_rate", "engagement_rate", "application_rate", "relevance_score"]:
                control_value = control_metrics[metric]
                treatment_value = variant_metrics[metric]
                
                if control_value > 0:
                    lift = ((treatment_value - control_value) / control_value) * 100
                else:
                    lift = 0.0 if treatment_value == 0 else float('inf')
                
                comparison["lifts"][metric] = {
                    "control": control_value,
                    "treatment": treatment_value,
                    "lift_percent": round(lift, 2) if lift != float('inf') else "inf"
                }
            
            comparisons[variant_name] = comparison
        
        return {
            "experiment_name": experiment_name,
            "control_variant": control_variant,
            "period": metrics["period"],
            "comparisons": comparisons
        }
    
    def get_experiment_summary(self, experiment_name: str) -> Dict[str, Any]:
        """
        Get high-level summary of experiment status.
        
        Args:
            experiment_name: Name of the experiment
        
        Returns:
            Summary dict with total users, variants, and key metrics
        """
        # Get total users assigned
        total_users = self.db.query(func.count(UserExperiment.id)).filter(
            UserExperiment.experiment_name == experiment_name
        ).scalar()
        
        # Get variant distribution
        variant_distribution = self.db.query(
            UserExperiment.variant_name,
            func.count(UserExperiment.id)
        ).filter(
            UserExperiment.experiment_name == experiment_name
        ).group_by(UserExperiment.variant_name).all()
        
        # Get total feedback
        total_feedback = self.db.query(func.count(Feedback.id)).filter(
            Feedback.experiment_name == experiment_name
        ).scalar()
        
        return {
            "experiment_name": experiment_name,
            "total_users": total_users or 0,
            "total_feedback": total_feedback or 0,
            "variant_distribution": {
                variant: count for variant, count in variant_distribution
            }
        }
    
    def get_all_experiments_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary for all experiments.
        
        Returns:
            List of experiment summaries
        """
        # Get all unique experiment names
        experiment_names = self.db.query(UserExperiment.experiment_name).distinct().all()
        
        summaries = []
        for (exp_name,) in experiment_names:
            summaries.append(self.get_experiment_summary(exp_name))
        
        return summaries
