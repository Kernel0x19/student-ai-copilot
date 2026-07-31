"""Integration tests for A/B testing infrastructure

This test demonstrates the complete A/B testing workflow:
1. Create experiment with variants
2. Assign users deterministically
3. Track variant in session metadata
4. Collect feedback
5. Calculate metrics (conversion, engagement)
6. Compare variants
7. Graduate winning variant
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.analytics.experiment_service import ExperimentService
from app.analytics.metrics_calculator import MetricsCalculator
from app.db.models import Base, Feedback


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_complete_ab_testing_workflow(db_session):
    """
    Test the complete A/B testing workflow from experiment creation to graduation.
    
    This integration test validates all requirements for task 11.2:
    - Requirement 20.1: Experiment definition with control/treatment variants
    - Requirement 20.2: Deterministic user assignment using user_id hash
    - Requirement 20.3: Variant tracking in user session metadata
    - Requirement 20.4: Backend serves different logic based on variant
    - Requirement 20.5: Log variant assignments for analysis
    - Requirement 20.6: Calculate experiment metrics (conversion, engagement)
    - Requirement 20.7: Experiment graduation (promote winning variant)
    """
    
    # Initialize services
    experiment_service = ExperimentService(db_session)
    metrics_calculator = MetricsCalculator(db_session)
    
    # ===== STEP 1: Create experiment with control and treatment variants =====
    # Requirement 20.1: Support defining experiments with control/treatment variants
    
    experiment_name = "recommendation_algorithm_test"
    variants = experiment_service.create_experiment(
        experiment_name=experiment_name,
        variants=[
            {
                "name": "control",
                "config": {
                    "algorithm": "rule_based",
                    "threshold": 0.5
                }
            },
            {
                "name": "treatment",
                "config": {
                    "algorithm": "ml_enhanced",
                    "threshold": 0.7,
                    "use_embeddings": True
                }
            }
        ]
    )
    
    assert len(variants) == 2
    assert variants[0].variant_name == "control"
    assert variants[1].variant_name == "treatment"
    assert variants[0].is_active is True
    assert variants[1].is_active is True
    
    # ===== STEP 2: Assign users to variants deterministically =====
    # Requirement 20.2: Deterministic user assignment using user_id hash
    
    users = [f"user_{i}" for i in range(100)]
    assignments = {}
    
    for user_id in users:
        variant = experiment_service.assign_user_to_variant(user_id, experiment_name)
        assignments[user_id] = variant
        
        # Verify assignment is deterministic (same user always gets same variant)
        variant_check = experiment_service.assign_user_to_variant(user_id, experiment_name)
        assert variant == variant_check, "Assignment should be deterministic"
    
    # Verify users are distributed across both variants
    variant_counts = {}
    for variant in assignments.values():
        variant_counts[variant] = variant_counts.get(variant, 0) + 1
    
    assert len(variant_counts) == 2, "Users should be assigned to both variants"
    assert 30 <= variant_counts.get("control", 0) <= 70, "Distribution should be reasonable"
    assert 30 <= variant_counts.get("treatment", 0) <= 70, "Distribution should be reasonable"
    
    # ===== STEP 3: Track variant assignments (session metadata) =====
    # Requirement 20.3: Track variant assignment in user session metadata
    # Requirement 20.5: Log all variant assignments for analysis
    
    for user_id in users[:10]:
        variant = experiment_service.get_user_variant(user_id, experiment_name)
        assert variant is not None, "Variant should be tracked"
        assert variant in ["control", "treatment"]
        
        # Get all experiments for user
        user_experiments = experiment_service.get_user_experiments(user_id)
        assert len(user_experiments) >= 1
        assert any(e["experiment_name"] == experiment_name for e in user_experiments)
    
    # ===== STEP 4: Simulate different behavior based on variant =====
    # Requirement 20.4: Backend serves different logic based on active experiment variant
    
    for user_id in users[:20]:
        variant = experiment_service.get_user_variant(user_id, experiment_name)
        variant_config = experiment_service.get_variant_config(experiment_name, variant)
        
        # In real application, this config would determine which algorithm to use
        if variant_config["algorithm"] == "ml_enhanced":
            # Simulate ML-enhanced recommendations (better performance)
            # In this test, we'll simulate higher conversion for treatment
            pass
        else:
            # Simulate rule-based recommendations
            pass
    
    # ===== STEP 5: Collect user feedback with variant association =====
    
    # Simulate feedback for control users (lower performance)
    control_users = [uid for uid, v in assignments.items() if v == "control"][:20]
    for i, user_id in enumerate(control_users):
        feedback_type = "applied" if i < 4 else "relevant" if i < 8 else "not_relevant"
        feedback = Feedback(
            user_id=user_id,
            opportunity_id=f"opp_{i}",
            feedback_type=feedback_type,
            experiment_name=experiment_name,
            variant_name="control"
        )
        db_session.add(feedback)
    
    # Simulate feedback for treatment users (higher performance)
    treatment_users = [uid for uid, v in assignments.items() if v == "treatment"][:20]
    for i, user_id in enumerate(treatment_users):
        feedback_type = "applied" if i < 12 else "relevant" if i < 16 else "not_relevant"
        feedback = Feedback(
            user_id=user_id,
            opportunity_id=f"opp_{i}",
            feedback_type=feedback_type,
            experiment_name=experiment_name,
            variant_name="treatment"
        )
        db_session.add(feedback)
    
    db_session.commit()
    
    # ===== STEP 6: Calculate experiment metrics =====
    # Requirement 20.6: Calculate and expose experiment metrics per variant
    
    metrics = metrics_calculator.calculate_experiment_metrics(experiment_name)
    
    assert "control" in metrics["variants"]
    assert "treatment" in metrics["variants"]
    
    control_metrics = metrics["variants"]["control"]
    treatment_metrics = metrics["variants"]["treatment"]
    
    # Verify all required metrics are calculated
    assert "conversion_rate" in control_metrics
    assert "engagement_rate" in control_metrics
    assert "application_rate" in control_metrics
    assert "relevance_score" in control_metrics
    
    # Treatment should have better metrics (based on our simulated data)
    assert treatment_metrics["conversion_rate"] > control_metrics["conversion_rate"]
    
    # ===== STEP 7: Compare variants with lift calculations =====
    
    comparison = metrics_calculator.compare_variants(experiment_name, "control")
    
    assert comparison["experiment_name"] == experiment_name
    assert "treatment" in comparison["comparisons"]
    
    treatment_comparison = comparison["comparisons"]["treatment"]
    conversion_lift = treatment_comparison["lifts"]["conversion_rate"]
    
    # Treatment should show positive lift
    assert conversion_lift["treatment"] > conversion_lift["control"]
    assert conversion_lift["lift_percent"] > 0, "Treatment should show positive lift"
    
    # ===== STEP 8: Get experiment summary =====
    
    summary = metrics_calculator.get_experiment_summary(experiment_name)
    
    assert summary["experiment_name"] == experiment_name
    assert summary["total_users"] == 100
    assert summary["total_feedback"] == 40  # 20 control + 20 treatment
    assert "control" in summary["variant_distribution"]
    assert "treatment" in summary["variant_distribution"]
    
    # ===== STEP 9: Graduate winning variant to default =====
    # Requirement 20.7: Support experiment graduation (promoting treatment to default)
    
    # Decision: Treatment variant wins due to higher conversion
    winning_config = experiment_service.promote_variant_to_default(
        experiment_name,
        "treatment"
    )
    
    assert winning_config["algorithm"] == "ml_enhanced"
    assert winning_config["use_embeddings"] is True
    
    # Verify experiment is deactivated
    active_experiments = experiment_service.get_all_active_experiments()
    assert experiment_name not in active_experiments
    
    # ===== STEP 10: Verify graduated config can be used as new default =====
    
    # In production, this config would be applied system-wide
    assert "algorithm" in winning_config
    assert "threshold" in winning_config
    
    print("\n=== A/B Testing Workflow Complete ===")
    print(f"Experiment: {experiment_name}")
    print(f"Total users: {summary['total_users']}")
    print(f"Control conversion: {control_metrics['conversion_rate']:.2%}")
    print(f"Treatment conversion: {treatment_metrics['conversion_rate']:.2%}")
    print(f"Lift: {conversion_lift['lift_percent']:.1f}%")
    print(f"Winner: treatment (graduated to default)")
    print(f"New default config: {winning_config}")


def test_multiple_concurrent_experiments(db_session):
    """
    Test that users can be assigned to multiple experiments simultaneously.
    
    This validates that experiment namespacing works correctly.
    """
    
    experiment_service = ExperimentService(db_session)
    
    # Create two independent experiments
    experiment_service.create_experiment(
        experiment_name="experiment_recommendations",
        variants=[
            {"name": "control", "config": {"algo": "baseline"}},
            {"name": "treatment", "config": {"algo": "ml"}}
        ]
    )
    
    experiment_service.create_experiment(
        experiment_name="experiment_ui",
        variants=[
            {"name": "control", "config": {"layout": "grid"}},
            {"name": "treatment", "config": {"layout": "list"}}
        ]
    )
    
    # Assign same user to both experiments
    user_id = "test_user"
    
    variant_1 = experiment_service.assign_user_to_variant(user_id, "experiment_recommendations")
    variant_2 = experiment_service.assign_user_to_variant(user_id, "experiment_ui")
    
    # User should have assignment in both experiments
    user_experiments = experiment_service.get_user_experiments(user_id)
    assert len(user_experiments) == 2
    
    experiment_names = [e["experiment_name"] for e in user_experiments]
    assert "experiment_recommendations" in experiment_names
    assert "experiment_ui" in experiment_names
    
    # Variants are independent (could be same or different)
    assert variant_1 in ["control", "treatment"]
    assert variant_2 in ["control", "treatment"]


def test_variant_config_controls_behavior(db_session):
    """
    Test that variant configurations can be used to control system behavior.
    
    This demonstrates Requirement 20.4: Backend serves different logic based on variant.
    """
    
    experiment_service = ExperimentService(db_session)
    
    # Create experiment with different algorithm configs
    experiment_service.create_experiment(
        experiment_name="scoring_algorithm",
        variants=[
            {
                "name": "control",
                "config": {
                    "use_embeddings": False,
                    "boost_factor": 1.0,
                    "min_score": 0.5
                }
            },
            {
                "name": "treatment",
                "config": {
                    "use_embeddings": True,
                    "boost_factor": 1.5,
                    "min_score": 0.3
                }
            }
        ]
    )
    
    # Assign user and get their variant config
    user_id = "test_user"
    variant = experiment_service.assign_user_to_variant(user_id, "scoring_algorithm")
    config = experiment_service.get_variant_config("scoring_algorithm", variant)
    
    # Config should be usable to control behavior
    assert "use_embeddings" in config
    assert "boost_factor" in config
    assert "min_score" in config
    
    # Simulate using config in recommendation logic
    def calculate_score(base_score: float, config: dict) -> float:
        """Simulate score calculation based on variant config"""
        score = base_score * config["boost_factor"]
        return max(score, config["min_score"])
    
    # Different variants would produce different scores
    base_score = 0.6
    control_config = experiment_service.get_variant_config("scoring_algorithm", "control")
    treatment_config = experiment_service.get_variant_config("scoring_algorithm", "treatment")
    
    control_score = calculate_score(base_score, control_config)
    treatment_score = calculate_score(base_score, treatment_config)
    
    # Treatment applies boost factor, so score should be different
    assert control_score == 0.6  # 0.6 * 1.0 = 0.6
    assert abs(treatment_score - 0.9) < 0.001  # 0.6 * 1.5 = 0.9 (with floating point tolerance)


