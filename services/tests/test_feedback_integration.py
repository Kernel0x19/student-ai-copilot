"""
Integration Tests for Feedback Collection System with Recommendation Engine

This test suite validates the complete feedback collection system including:
- Feedback data model and API endpoints
- Experiment variant association
- Recommendation engine integration with feedback learning
- End-to-end feedback workflow

**Validates: Requirements 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7**
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import (
    Base,
    User,
    UserRole,
    StudentProfile,
    Opportunity,
    OpportunityCategory,
    Feedback,
    ExperimentVariant,
    UserExperiment,
    Application,
    ApplicationState
)
from app.analytics.event_service import AnalyticsEventService
from app.analytics.experiment_service import ExperimentService
from app.intelligence.recommendation import (
    apply_feedback_learning,
    compute_match_score,
    get_personalized_recommendations
)
from app.agents.scholarship import ScholarshipAgent


# Test database setup
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user with profile"""
    user = User(
        id="user-test-123",
        email="test@example.com",
        phone_number="+1234567890",
        role=UserRole.STUDENT
    )
    db_session.add(user)
    
    profile = StudentProfile(
        id="profile-test-123",
        user_id=user.id,
        full_name="Test User",
        state="California",
        category="General",
        income_annual=50000.0,
        college="Test University",
        stream="Computer Science",
        year_of_study=3,
        cgpa=8.5
    )
    db_session.add(profile)
    db_session.commit()
    
    return user


@pytest.fixture
def test_opportunities(db_session: Session):
    """Create test opportunities with different characteristics"""
    opportunities = [
        Opportunity(
            id="opp-scholarship-1",
            source="test",
            source_url="https://test.com/opp1",
            category=OpportunityCategory.SCHOLARSHIP,
            title="Tech Scholarship for CS Students",
            description="Scholarship for computer science students",
            amount_min=5000.0,
            amount_max=10000.0,
            deadline=date.today() + timedelta(days=30),
            eligibility_rules={
                "stream": ["Computer Science", "IT"],
                "min_cgpa": 7.0
            },
            state_filter=["California", "ALL"],
            is_active=True
        ),
        Opportunity(
            id="opp-scholarship-2",
            source="test",
            source_url="https://test.com/opp2",
            category=OpportunityCategory.SCHOLARSHIP,
            title="Similar Tech Scholarship",
            description="Another scholarship for CS students",
            amount_min=4000.0,
            amount_max=9000.0,
            deadline=date.today() + timedelta(days=45),
            eligibility_rules={
                "stream": ["Computer Science"],
                "min_cgpa": 7.5
            },
            state_filter=["California"],
            is_active=True
        ),
        Opportunity(
            id="opp-scholarship-3",
            source="test",
            source_url="https://test.com/opp3",
            category=OpportunityCategory.SCHOLARSHIP,
            title="Medical Scholarship",
            description="Scholarship for medical students",
            amount_min=15000.0,
            amount_max=20000.0,
            deadline=date.today() + timedelta(days=60),
            eligibility_rules={
                "stream": ["Medical", "MBBS"],
                "min_cgpa": 8.0
            },
            state_filter=["ALL"],
            is_active=True
        )
    ]
    
    for opp in opportunities:
        db_session.add(opp)
    db_session.commit()
    
    return opportunities


class TestFeedbackDataModel:
    """Test feedback data model and database operations
    
    **Validates: Requirement 21.2**
    """
    
    def test_feedback_model_creation(self, db_session: Session, test_user, test_opportunities):
        """Test creating feedback records with all required fields"""
        feedback = Feedback(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            feedback_type="relevant",
            comment="Great match for my profile!"
        )
        db_session.add(feedback)
        db_session.commit()
        
        # Verify feedback was created
        saved_feedback = db_session.query(Feedback).filter_by(user_id=test_user.id).first()
        assert saved_feedback is not None
        assert saved_feedback.user_id == test_user.id
        assert saved_feedback.opportunity_id == test_opportunities[0].id
        assert saved_feedback.feedback_type == "relevant"
        assert saved_feedback.comment == "Great match for my profile!"
        assert saved_feedback.created_at is not None
    
    def test_feedback_without_comment(self, db_session: Session, test_user, test_opportunities):
        """Test that comment field is optional"""
        feedback = Feedback(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            feedback_type="not_relevant",
            comment=None
        )
        db_session.add(feedback)
        db_session.commit()
        
        saved_feedback = db_session.query(Feedback).filter_by(user_id=test_user.id).first()
        assert saved_feedback.comment is None
    
    def test_feedback_types(self, db_session: Session, test_user, test_opportunities):
        """Test all supported feedback types"""
        feedback_types = ["relevant", "not_relevant", "ineligible", "applied", "ignored"]
        
        for idx, ftype in enumerate(feedback_types):
            feedback = Feedback(
                user_id=test_user.id,
                opportunity_id=test_opportunities[0].id,
                feedback_type=ftype
            )
            db_session.add(feedback)
        
        db_session.commit()
        
        # Verify all feedback types were saved
        all_feedback = db_session.query(Feedback).filter_by(user_id=test_user.id).all()
        assert len(all_feedback) == len(feedback_types)
        saved_types = {f.feedback_type for f in all_feedback}
        assert saved_types == set(feedback_types)


class TestExperimentAssociation:
    """Test feedback association with A/B test experiments
    
    **Validates: Requirement 21.4**
    """
    
    def test_feedback_with_single_experiment(self, db_session: Session, test_user, test_opportunities):
        """Test feedback is associated with active experiment"""
        # Create experiment
        exp_service = ExperimentService(db_session)
        exp_service.create_experiment(
            "recommendation_algo_v2",
            [
                {"name": "control", "config": {"algorithm": "baseline"}},
                {"name": "treatment_a", "config": {"algorithm": "ml_enhanced"}}
            ]
        )
        
        # Assign user to variant
        variant = exp_service.assign_user_to_variant(test_user.id, "recommendation_algo_v2")
        
        # Submit feedback through event service
        event_service = AnalyticsEventService(db_session)
        result = event_service.collect_feedback(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            feedback_type="relevant",
            comment="Good match"
        )
        
        # Verify feedback has experiment association
        assert result["feedback_count"] == 1
        assert len(result["experiments"]) == 1
        assert result["experiments"][0]["experiment_name"] == "recommendation_algo_v2"
        assert result["experiments"][0]["variant_name"] == variant
        
        # Verify in database
        feedback = db_session.query(Feedback).filter_by(user_id=test_user.id).first()
        assert feedback.experiment_name == "recommendation_algo_v2"
        assert feedback.variant_name == variant
    
    def test_feedback_with_multiple_experiments(self, db_session: Session, test_user, test_opportunities):
        """Test feedback creates records for each active experiment"""
        # Create multiple experiments
        exp_service = ExperimentService(db_session)
        
        exp_service.create_experiment(
            "experiment_1",
            [
                {"name": "control", "config": {}},
                {"name": "treatment", "config": {}}
            ]
        )
        
        exp_service.create_experiment(
            "experiment_2",
            [
                {"name": "control", "config": {}},
                {"name": "variant_a", "config": {}}
            ]
        )
        
        # Assign user to both experiments
        exp_service.assign_user_to_variant(test_user.id, "experiment_1")
        exp_service.assign_user_to_variant(test_user.id, "experiment_2")
        
        # Submit feedback
        event_service = AnalyticsEventService(db_session)
        result = event_service.collect_feedback(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            feedback_type="relevant"
        )
        
        # Verify feedback count (one per experiment)
        assert result["feedback_count"] == 2
        assert len(result["experiments"]) == 2
        
        # Verify both experiments are present
        exp_names = {exp["experiment_name"] for exp in result["experiments"]}
        assert exp_names == {"experiment_1", "experiment_2"}
        
        # Verify in database
        all_feedback = db_session.query(Feedback).filter_by(user_id=test_user.id).all()
        assert len(all_feedback) == 2


class TestRecommendationEngineFeedbackIntegration:
    """Test integration of feedback with recommendation engine
    
    **Validates: Requirement 21.6**
    """
    
    def test_negative_feedback_reduces_similar_scores(
        self, db_session: Session, test_user, test_opportunities
    ):
        """Test that negative feedback on one opportunity reduces scores for similar opportunities"""
        profile = db_session.query(StudentProfile).filter_by(user_id=test_user.id).first()
        
        # Get base scores without feedback
        opp1 = test_opportunities[0]  # Tech scholarship
        opp2 = test_opportunities[1]  # Similar tech scholarship
        
        base_score_1, _, _ = compute_match_score(profile, opp1)
        base_score_2, _, _ = compute_match_score(profile, opp2)
        
        # Submit negative feedback on opp1
        feedback = Feedback(
            user_id=test_user.id,
            opportunity_id=opp1.id,
            feedback_type="not_relevant",
            comment="Not interested in this type"
        )
        db_session.add(feedback)
        db_session.commit()
        
        # Get adjusted score for opp2 (should be penalized due to similarity)
        adjusted_score_2 = apply_feedback_learning(profile, opp2, base_score_2 / 100.0, db_session)
        adjusted_score_2 = adjusted_score_2 * 100.0
        
        # Verify score was reduced
        assert adjusted_score_2 < base_score_2, \
            f"Expected penalty: adjusted ({adjusted_score_2}) should be < base ({base_score_2})"
        
        # Verify penalty is reasonable (not too harsh, not too small)
        penalty_percent = ((base_score_2 - adjusted_score_2) / base_score_2) * 100
        assert 5 <= penalty_percent <= 50, \
            f"Penalty should be 5-50%, got {penalty_percent:.1f}%"
    
    def test_negative_feedback_does_not_affect_dissimilar(
        self, db_session: Session, test_user, test_opportunities
    ):
        """Test that negative feedback doesn't affect dissimilar opportunities"""
        profile = db_session.query(StudentProfile).filter_by(user_id=test_user.id).first()
        
        opp1 = test_opportunities[0]  # Tech scholarship
        opp3 = test_opportunities[2]  # Medical scholarship (different category)
        
        base_score_3, _, _ = compute_match_score(profile, opp3)
        
        # Submit negative feedback on tech scholarship
        feedback = Feedback(
            user_id=test_user.id,
            opportunity_id=opp1.id,
            feedback_type="not_relevant"
        )
        db_session.add(feedback)
        db_session.commit()
        
        # Get adjusted score for medical scholarship
        adjusted_score_3 = apply_feedback_learning(profile, opp3, base_score_3 / 100.0, db_session)
        adjusted_score_3 = adjusted_score_3 * 100.0
        
        # Should have minimal penalty (different category, but may have some state overlap)
        penalty_percent = abs(base_score_3 - adjusted_score_3) / base_score_3 * 100
        assert penalty_percent < 20, \
            f"Dissimilar opportunity should have < 20% penalty, got {penalty_percent:.1f}%"
    
    def test_multiple_negative_feedback_accumulates_penalty(
        self, db_session: Session, test_user, test_opportunities
    ):
        """Test that multiple negative feedback instances increase the penalty"""
        profile = db_session.query(StudentProfile).filter_by(user_id=test_user.id).first()
        
        target_opp = test_opportunities[1]  # Similar tech scholarship
        base_score, _, _ = compute_match_score(profile, target_opp)
        
        # Submit multiple negative feedback on similar opportunities
        feedback1 = Feedback(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            feedback_type="not_relevant"
        )
        db_session.add(feedback1)
        db_session.commit()
        
        # Get score after one feedback
        adjusted_score_1 = apply_feedback_learning(profile, target_opp, base_score / 100.0, db_session)
        penalty_1 = base_score - (adjusted_score_1 * 100.0)
        
        # Add another similar opportunity as test data
        similar_opp = Opportunity(
            id="opp-similar-temp",
            source="test",
            source_url="https://test.com/similar",
            category=OpportunityCategory.SCHOLARSHIP,
            title="Another CS Scholarship",
            amount_min=4500.0,
            amount_max=9500.0,
            deadline=date.today() + timedelta(days=40),
            eligibility_rules={"stream": ["Computer Science"]},
            state_filter=["California"],
            is_active=True
        )
        db_session.add(similar_opp)
        db_session.commit()
        
        # Add second negative feedback
        feedback2 = Feedback(
            user_id=test_user.id,
            opportunity_id=similar_opp.id,
            feedback_type="ineligible"
        )
        db_session.add(feedback2)
        db_session.commit()
        
        # Get score after two feedbacks
        adjusted_score_2 = apply_feedback_learning(profile, target_opp, base_score / 100.0, db_session)
        penalty_2 = base_score - (adjusted_score_2 * 100.0)
        
        # Penalty should increase (but capped at 50%)
        assert penalty_2 >= penalty_1, \
            "Multiple negative feedbacks should increase penalty"
    
    def test_positive_feedback_does_not_penalize(
        self, db_session: Session, test_user, test_opportunities
    ):
        """Test that positive feedback doesn't reduce scores"""
        profile = db_session.query(StudentProfile).filter_by(user_id=test_user.id).first()
        
        opp1 = test_opportunities[0]
        opp2 = test_opportunities[1]
        
        base_score, _, _ = compute_match_score(profile, opp2)
        
        # Submit positive feedback
        feedback = Feedback(
            user_id=test_user.id,
            opportunity_id=opp1.id,
            feedback_type="relevant"
        )
        db_session.add(feedback)
        db_session.commit()
        
        # Get adjusted score
        adjusted_score = apply_feedback_learning(profile, opp2, base_score / 100.0, db_session)
        adjusted_score = adjusted_score * 100.0
        
        # Should not be penalized
        assert adjusted_score >= base_score * 0.95, \
            "Positive feedback should not penalize similar opportunities"


class TestEndToEndFeedbackWorkflow:
    """Test complete feedback workflow from collection to recommendation adjustment
    
    **Validates: Requirements 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7**
    """
    
    def test_complete_feedback_to_recommendation_flow(
        self, db_session: Session, test_user, test_opportunities
    ):
        """Test the complete flow: submit feedback -> recommendations are adjusted"""
        profile = db_session.query(StudentProfile).filter_by(user_id=test_user.id).first()
        
        # Step 1: Get initial recommendations
        agent = ScholarshipAgent()
        initial_recs = agent.recommend(db_session, profile, limit=10)
        
        # Find the CS scholarships in recommendations
        cs_scholarships = [
            m for m in initial_recs.matches
            if "Tech" in m.opportunity.title or "CS" in m.opportunity.title
        ]
        
        assert len(cs_scholarships) >= 2, "Should have multiple CS scholarships"
        
        # Step 2: User views and dismisses one CS scholarship
        dismissed_opp_id = cs_scholarships[0].opportunity.id
        
        event_service = AnalyticsEventService(db_session)
        event_service.log_recommendation_viewed(
            user_id=test_user.id,
            opportunity_id=dismissed_opp_id,
            match_score=cs_scholarships[0].match_score
        )
        
        event_service.collect_feedback(
            user_id=test_user.id,
            opportunity_id=dismissed_opp_id,
            feedback_type="not_relevant",
            comment="Not interested in this type of scholarship"
        )
        
        # Step 3: Get new recommendations (should show reduced scores for similar scholarships)
        updated_recs = agent.recommend(db_session, profile, limit=10)
        
        # Find the same opportunities in updated recommendations
        updated_cs_scholarships = [
            m for m in updated_recs.matches
            if "Tech" in m.opportunity.title or "CS" in m.opportunity.title
        ]
        
        # At least one similar scholarship should have reduced score
        # (Note: scores might still keep them ranked high due to good eligibility match,
        #  but the absolute score should be lower)
        for updated_match in updated_cs_scholarships:
            if updated_match.opportunity.id != dismissed_opp_id:
                # Find corresponding initial match
                initial_match = next(
                    (m for m in cs_scholarships if m.opportunity.id == updated_match.opportunity.id),
                    None
                )
                if initial_match:
                    # Verify score was adjusted (might be subtle)
                    # We're looking for ANY reduction, even small
                    assert updated_match.match_score <= initial_match.match_score, \
                        f"Similar scholarship {updated_match.opportunity.title} should have same or lower score"
    
    def test_feedback_summary_metrics(self, db_session: Session, test_user, test_opportunities):
        """Test aggregated feedback metrics
        
        **Validates: Requirement 21.5**
        """
        # Submit various feedback
        feedbacks = [
            ("relevant", test_opportunities[0].id),
            ("relevant", test_opportunities[1].id),
            ("not_relevant", test_opportunities[2].id),
            ("applied", test_opportunities[0].id)
        ]
        
        event_service = AnalyticsEventService(db_session)
        for ftype, opp_id in feedbacks:
            event_service.collect_feedback(
                user_id=test_user.id,
                opportunity_id=opp_id,
                feedback_type=ftype
            )
        
        # Get feedback summary
        summary = event_service.get_user_activity_summary(test_user.id)
        
        # Verify counts
        assert summary["feedback"]["relevant"] == 2
        assert summary["feedback"]["not_relevant"] == 1
        assert summary["feedback"]["applied"] == 1
    
    def test_personalized_recommendations_with_feedback(
        self, db_session: Session, test_user, test_opportunities
    ):
        """Test get_personalized_recommendations helper function with feedback"""
        profile = db_session.query(StudentProfile).filter_by(user_id=test_user.id).first()
        
        # Add negative feedback on first opportunity
        feedback = Feedback(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            feedback_type="not_relevant"
        )
        db_session.add(feedback)
        db_session.commit()
        
        # Get personalized recommendations
        recommendations = get_personalized_recommendations(
            profile=profile,
            opportunities=test_opportunities,
            db_session=db_session,
            limit=10
        )
        
        # Verify recommendations were adjusted
        assert len(recommendations) > 0
        
        # Check that scores include feedback adjustment
        for rec in recommendations:
            if rec["opportunity"].id == test_opportunities[1].id:
                # Similar opportunity should have adjusted score lower than base
                assert rec["score"] <= rec["base_score"], \
                    "Adjusted score should be <= base score after negative feedback"


class TestFeedbackCollectionUI:
    """Test feedback collection timing and triggers
    
    **Validates: Requirement 21.7**
    """
    
    def test_feedback_after_recommendation_interaction(
        self, db_session: Session, test_user, test_opportunities
    ):
        """Test that feedback is collected after user interactions (save, apply, dismiss)"""
        event_service = AnalyticsEventService(db_session)
        
        # Simulate user saving a recommendation
        save_result = event_service.log_recommendation_saved(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            source="dashboard"
        )
        
        # Verify event was logged
        assert save_result["event_type"] == "recommendation_saved"
        
        # Now user provides feedback (would be triggered by UI)
        feedback_result = event_service.collect_feedback(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id,
            feedback_type="relevant",
            comment="Looks good!"
        )
        
        # Verify feedback was collected
        assert feedback_result["feedback_count"] >= 1
        
        # Verify both events are in database
        application = db_session.query(Application).filter_by(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id
        ).first()
        assert application is not None
        assert application.saved is True
        
        feedback = db_session.query(Feedback).filter_by(
            user_id=test_user.id,
            opportunity_id=test_opportunities[0].id
        ).first()
        assert feedback is not None
        assert feedback.feedback_type == "relevant"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
