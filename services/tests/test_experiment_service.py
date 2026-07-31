"""Unit tests for ExperimentService

Tests cover:
- Experiment creation with control/treatment variants
- Deterministic user assignment using user_id hash
- Variant tracking and retrieval
- Experiment graduation
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.analytics.experiment_service import ExperimentService
from app.db.models import Base, ExperimentVariant, UserExperiment


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def experiment_service(db_session):
    """Create ExperimentService instance"""
    return ExperimentService(db_session)


def test_create_experiment(experiment_service, db_session):
    """Test creating an experiment with control and treatment variants"""
    variants = experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {"algorithm": "baseline"}},
            {"name": "treatment_a", "config": {"algorithm": "ml_enhanced"}}
        ]
    )
    
    assert len(variants) == 2
    assert variants[0].experiment_name == "test_experiment"
    assert variants[0].variant_name == "control"
    assert variants[0].is_active is True
    assert variants[0].config == {"algorithm": "baseline"}
    
    assert variants[1].variant_name == "treatment_a"
    assert variants[1].config == {"algorithm": "ml_enhanced"}


def test_create_duplicate_experiment_raises_error(experiment_service):
    """Test that creating a duplicate experiment raises ValueError"""
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    with pytest.raises(ValueError, match="already exists"):
        experiment_service.create_experiment(
            experiment_name="test_experiment",
            variants=[
                {"name": "control", "config": {}},
                {"name": "treatment", "config": {}}
            ]
        )


def test_deterministic_user_assignment(experiment_service, db_session):
    """Test that user assignment is deterministic based on user_id hash"""
    # Create experiment
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    user_id = "user123"
    
    # Assign user multiple times
    variant1 = experiment_service.assign_user_to_variant(user_id, "test_experiment")
    variant2 = experiment_service.assign_user_to_variant(user_id, "test_experiment")
    variant3 = experiment_service.assign_user_to_variant(user_id, "test_experiment")
    
    # All assignments should be the same
    assert variant1 == variant2 == variant3
    
    # Verify only one assignment record was created
    assignments = db_session.query(UserExperiment).filter_by(
        user_id=user_id,
        experiment_name="test_experiment"
    ).all()
    assert len(assignments) == 1


def test_user_assignment_distribution(experiment_service, db_session):
    """Test that users are evenly distributed across variants"""
    # Create experiment with two variants
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    # Assign 100 users
    variant_counts = {"control": 0, "treatment": 0}
    for i in range(100):
        user_id = f"user{i}"
        variant = experiment_service.assign_user_to_variant(user_id, "test_experiment")
        variant_counts[variant] += 1
    
    # Check distribution is roughly even (within 30-70% range)
    assert 30 <= variant_counts["control"] <= 70
    assert 30 <= variant_counts["treatment"] <= 70


def test_different_experiments_different_assignments(experiment_service):
    """Test that same user can get different variants in different experiments"""
    # Create two experiments
    experiment_service.create_experiment(
        experiment_name="experiment_a",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    experiment_service.create_experiment(
        experiment_name="experiment_b",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    user_id = "user123"
    
    # Assign to both experiments
    variant_a = experiment_service.assign_user_to_variant(user_id, "experiment_a")
    variant_b = experiment_service.assign_user_to_variant(user_id, "experiment_b")
    
    # Variants are independent (could be same or different)
    assert variant_a in ["control", "treatment"]
    assert variant_b in ["control", "treatment"]


def test_get_user_variant(experiment_service):
    """Test retrieving user's assigned variant"""
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    user_id = "user123"
    
    # Before assignment, should return None
    variant = experiment_service.get_user_variant(user_id, "test_experiment")
    assert variant is None
    
    # After assignment, should return the variant
    assigned_variant = experiment_service.assign_user_to_variant(user_id, "test_experiment")
    retrieved_variant = experiment_service.get_user_variant(user_id, "test_experiment")
    assert retrieved_variant == assigned_variant


def test_get_variant_config(experiment_service):
    """Test retrieving variant configuration"""
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {"algorithm": "baseline", "threshold": 0.5}},
            {"name": "treatment", "config": {"algorithm": "ml_enhanced", "threshold": 0.7}}
        ]
    )
    
    control_config = experiment_service.get_variant_config("test_experiment", "control")
    assert control_config == {"algorithm": "baseline", "threshold": 0.5}
    
    treatment_config = experiment_service.get_variant_config("test_experiment", "treatment")
    assert treatment_config == {"algorithm": "ml_enhanced", "threshold": 0.7}
    
    # Non-existent variant should return None
    invalid_config = experiment_service.get_variant_config("test_experiment", "invalid")
    assert invalid_config is None


def test_deactivate_experiment(experiment_service, db_session):
    """Test deactivating an experiment"""
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    # Verify variants are active
    variants = db_session.query(ExperimentVariant).filter_by(
        experiment_name="test_experiment"
    ).all()
    assert all(v.is_active for v in variants)
    
    # Deactivate
    count = experiment_service.deactivate_experiment("test_experiment")
    assert count == 2
    
    # Verify variants are now inactive
    variants = db_session.query(ExperimentVariant).filter_by(
        experiment_name="test_experiment"
    ).all()
    assert all(not v.is_active for v in variants)


def test_promote_variant_to_default(experiment_service):
    """Test promoting a winning variant to default"""
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {"algorithm": "baseline"}},
            {"name": "treatment", "config": {"algorithm": "ml_enhanced"}}
        ]
    )
    
    # Promote treatment variant
    config = experiment_service.promote_variant_to_default("test_experiment", "treatment")
    
    assert config == {"algorithm": "ml_enhanced"}
    
    # Verify experiment is deactivated
    active_experiments = experiment_service.get_all_active_experiments()
    assert "test_experiment" not in active_experiments


def test_promote_invalid_variant_raises_error(experiment_service):
    """Test that promoting a non-existent variant raises ValueError"""
    experiment_service.create_experiment(
        experiment_name="test_experiment",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    with pytest.raises(ValueError, match="not found"):
        experiment_service.promote_variant_to_default("test_experiment", "invalid_variant")


def test_get_all_active_experiments(experiment_service):
    """Test retrieving all active experiments"""
    experiment_service.create_experiment(
        experiment_name="experiment_a",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    experiment_service.create_experiment(
        experiment_name="experiment_b",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    active_experiments = experiment_service.get_all_active_experiments()
    assert "experiment_a" in active_experiments
    assert "experiment_b" in active_experiments
    assert len(active_experiments) == 2
    
    # Deactivate one
    experiment_service.deactivate_experiment("experiment_a")
    
    active_experiments = experiment_service.get_all_active_experiments()
    assert "experiment_a" not in active_experiments
    assert "experiment_b" in active_experiments
    assert len(active_experiments) == 1


def test_get_user_experiments(experiment_service):
    """Test retrieving all experiments a user is assigned to"""
    experiment_service.create_experiment(
        experiment_name="experiment_a",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    experiment_service.create_experiment(
        experiment_name="experiment_b",
        variants=[
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}}
        ]
    )
    
    user_id = "user123"
    
    # Assign to both experiments
    experiment_service.assign_user_to_variant(user_id, "experiment_a")
    experiment_service.assign_user_to_variant(user_id, "experiment_b")
    
    # Get user's assignments
    assignments = experiment_service.get_user_experiments(user_id)
    
    assert len(assignments) == 2
    experiment_names = [a["experiment_name"] for a in assignments]
    assert "experiment_a" in experiment_names
    assert "experiment_b" in experiment_names


def test_assign_to_nonexistent_experiment_raises_error(experiment_service):
    """Test that assigning to a non-existent experiment raises ValueError"""
    with pytest.raises(ValueError, match="No active variants found"):
        experiment_service.assign_user_to_variant("user123", "nonexistent_experiment")

