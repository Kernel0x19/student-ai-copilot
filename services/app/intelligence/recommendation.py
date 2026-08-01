from app.db.models import Opportunity, StudentProfile, Feedback
from app.intelligence.eligibility import evaluate_eligibility
from sqlalchemy.orm import Session
from typing import Optional


WEIGHTS = {
    "eligibility": 0.55,
    "deadline_urgency": 0.15,
    "profile_completeness": 0.15,
    "preference_match": 0.15,
}


def _deadline_score(opp: Opportunity) -> float:
    if not opp.deadline:
        return 0.5
    from datetime import date

    days = (opp.deadline - date.today()).days
    if days < 0:
        return 0.0
    if days <= 14:
        return 1.0
    if days <= 30:
        return 0.8
    if days <= 60:
        return 0.6
    return 0.4


def _profile_completeness(profile: StudentProfile | None) -> float:
    if not profile:
        return 0.0
    fields = [
        profile.full_name,
        profile.state,
        profile.category,
        profile.college,
        profile.stream,
        profile.year_of_study,
        profile.cgpa or profile.percentage_12th,
        profile.income_annual,
    ]
    return sum(1 for f in fields if f is not None) / len(fields)


def _preference_match(profile: StudentProfile | None, opp: Opportunity) -> float:
    if not profile or not profile.preferences:
        return 0.5
    prefs = profile.preferences
    score = 0.5
    if preferred_states := prefs.get("states"):
        if opp.state_filter and ("ALL" in opp.state_filter or any(s in opp.state_filter for s in preferred_states)):
            score += 0.3
    if min_amount := prefs.get("min_amount"):
        if opp.amount_max and opp.amount_max >= min_amount:
            score += 0.2
    return min(score, 1.0)


def compute_match_score(profile: StudentProfile | None, opp: Opportunity) -> tuple[float, dict, list[str]]:
    eligibility = evaluate_eligibility(profile, opp.eligibility_rules or {})
    reasons = []

    if eligibility["eligible"]:
        reasons.extend([f"✓ {p}" for p in eligibility["passed"][:3]])
    else:
        reasons.extend([f"✗ {f}" for f in eligibility["failed"][:2]])

    if eligibility["warnings"]:
        reasons.append(f"⚠ {eligibility['warnings'][0]}")

    elig_score = eligibility["score"] if eligibility["eligible"] else eligibility["score"] * 0.3
    deadline = _deadline_score(opp)
    completeness = _profile_completeness(profile)
    pref = _preference_match(profile, opp)

    match = (
        WEIGHTS["eligibility"] * elig_score
        + WEIGHTS["deadline_urgency"] * deadline
        + WEIGHTS["profile_completeness"] * completeness
        + WEIGHTS["preference_match"] * pref
    )

    if opp.deadline:
        from datetime import date

        days = (opp.deadline - date.today()).days
        if days <= 14:
            reasons.append(f"Deadline in {days} days — apply soon")

    return round(match * 100, 1), eligibility, reasons


def compute_readiness_score(profile: StudentProfile | None) -> float:
    if not profile:
        return 0.0
    base = _profile_completeness(profile) * 60
    doc_bonus = min(len(profile.documents or []) * 10, 30)
    skill_bonus = min(len(profile.skills or []) * 2, 10)
    return round(min(base + doc_bonus + skill_bonus, 100), 1)


def apply_feedback_learning(
    profile: StudentProfile | None,
    opportunity: Opportunity,
    base_score: float,
    db_session: Optional[Session] = None
) -> float:
    """
    Adjust recommendation score based on user's historical feedback.
    
    This implements learning from negative feedback (not_relevant, ineligible)
    to improve future recommendations by penalizing similar opportunities.
    
    **Validates: Requirement 21.6** - Use negative feedback to improve future recommendations
    
    Args:
        profile: User's student profile
        opportunity: Opportunity being scored
        base_score: Base match score before feedback adjustment
        db_session: Database session for querying feedback
    
    Returns:
        Adjusted score (reduced for opportunities similar to negatively rated ones)
    """
    if not profile or not db_session:
        return base_score
    
    # Query user's negative feedback
    negative_feedback = db_session.query(Feedback).filter(
        Feedback.user_id == profile.user_id,
        Feedback.feedback_type.in_(["not_relevant", "ineligible"])
    ).all()
    
    if not negative_feedback:
        return base_score
    
    # Calculate penalty based on similarity to negatively rated opportunities
    penalty = 0.0
    
    for feedback in negative_feedback:
        # Get the negatively rated opportunity
        neg_opp = db_session.query(Opportunity).filter(
            Opportunity.id == feedback.opportunity_id
        ).first()
        
        if not neg_opp:
            continue
        
        # Calculate similarity (simple heuristic based on category and amount)
        similarity_score = 0.0
        
        # Category match
        if neg_opp.category == opportunity.category:
            similarity_score += 0.5
        
        # Amount range overlap (if both have amounts)
        if neg_opp.amount_min and neg_opp.amount_max and opportunity.amount_min and opportunity.amount_max:
            # Check if ranges overlap
            if not (neg_opp.amount_max < opportunity.amount_min or neg_opp.amount_min > opportunity.amount_max):
                similarity_score += 0.3
        
        # State filter overlap
        if neg_opp.state_filter and opportunity.state_filter:
            neg_states = set(neg_opp.state_filter)
            opp_states = set(opportunity.state_filter)
            if neg_states & opp_states:  # If there's any intersection
                similarity_score += 0.2
        
        # Apply penalty proportional to similarity
        # Higher similarity = higher penalty (max 20% reduction per similar negative feedback)
        penalty += similarity_score * 0.20
    
    # Cap total penalty at 50% to avoid over-penalizing
    penalty = min(penalty, 0.50)
    
    # Apply penalty
    adjusted_score = base_score * (1.0 - penalty)
    
    return adjusted_score


def get_personalized_recommendations(
    profile: StudentProfile,
    opportunities: list[Opportunity],
    db_session: Optional[Session] = None,
    limit: int = 20
) -> list[dict]:
    """
    Get personalized opportunity recommendations with feedback-based learning.
    
    This is a convenience function that computes match scores for multiple
    opportunities and applies feedback learning to improve recommendations.
    
    Args:
        profile: User's student profile
        opportunities: List of opportunities to score
        db_session: Database session for feedback queries
        limit: Maximum number of recommendations to return
    
    Returns:
        List of opportunities with scores, sorted by adjusted score
    """
    scored_opportunities = []
    
    for opp in opportunities:
        # Compute base match score
        base_score, eligibility, reasons = compute_match_score(profile, opp)
        
        # Apply feedback learning if db_session available
        if db_session:
            adjusted_score = apply_feedback_learning(profile, opp, base_score / 100.0, db_session)
            final_score = adjusted_score * 100.0
        else:
            final_score = base_score
        
        scored_opportunities.append({
            "opportunity": opp,
            "score": round(final_score, 1),
            "base_score": base_score,
            "eligibility": eligibility,
            "reasons": reasons
        })
    
    # Sort by adjusted score (descending)
    scored_opportunities.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top N
    return scored_opportunities[:limit]
