from app.db.models import StudentProfile


def evaluate_eligibility(profile: StudentProfile | None, rules: dict) -> dict:
    """Deterministic rules engine for government scheme eligibility."""
    if not profile:
        return {"eligible": False, "score": 0.0, "passed": [], "failed": ["Profile incomplete"], "warnings": []}

    passed, failed, warnings = [], [], []
    score_factors = []

    if categories := rules.get("category"):
        if profile.category and profile.category in categories:
            passed.append(f"Category {profile.category} matches")
            score_factors.append(1.0)
        else:
            failed.append(f"Category must be one of: {', '.join(categories)}")

    if max_income := rules.get("max_income"):
        if profile.income_annual is not None:
            if profile.income_annual <= max_income:
                passed.append(f"Income ₹{profile.income_annual:,.0f} within limit ₹{max_income:,.0f}")
                score_factors.append(1.0)
            else:
                failed.append(f"Income exceeds ₹{max_income:,.0f} limit")
        else:
            warnings.append("Income not provided — cannot verify income eligibility")

    if min_cgpa := rules.get("min_cgpa"):
        if profile.cgpa is not None:
            if profile.cgpa >= min_cgpa:
                passed.append(f"CGPA {profile.cgpa} meets minimum {min_cgpa}")
                score_factors.append(1.0)
            else:
                failed.append(f"CGPA {profile.cgpa} below minimum {min_cgpa}")
        else:
            warnings.append("CGPA not provided")

    if min_pct := rules.get("min_percentage_12th"):
        if profile.percentage_12th is not None:
            if profile.percentage_12th >= min_pct:
                passed.append(f"12th {profile.percentage_12th}% meets minimum {min_pct}%")
                score_factors.append(1.0)
            else:
                failed.append(f"12th percentage below {min_pct}%")
        else:
            warnings.append("12th percentage not provided")

    if gender_rules := rules.get("gender"):
        if profile.gender:
            if profile.gender in gender_rules:
                passed.append(f"Gender {profile.gender} eligible")
                score_factors.append(1.0)
            else:
                failed.append(f"Scheme restricted to: {', '.join(gender_rules)}")
        else:
            warnings.append("Gender not provided")

    if states := rules.get("states"):
        if "ALL" in states:
            passed.append("Open to all states")
            score_factors.append(0.5)
        elif profile.state:
            if profile.state in states:
                passed.append(f"State {profile.state} eligible")
                score_factors.append(1.0)
            else:
                failed.append(f"Restricted to: {', '.join(states)}")

    if streams := rules.get("streams"):
        if profile.stream:
            if any(s.lower() in profile.stream.lower() for s in streams):
                passed.append(f"Stream {profile.stream} matches")
                score_factors.append(1.0)
            else:
                failed.append(f"Stream must be: {', '.join(streams)}")
        else:
            warnings.append("Stream not provided")

    if degrees := rules.get("degree") or rules.get("degrees"):
        if profile.degree:
            if any(degree.lower() in profile.degree.lower() for degree in degrees):
                passed.append(f"Degree {profile.degree} matches")
                score_factors.append(1.0)
            else:
                failed.append(f"Degree must be: {', '.join(degrees)}")
        else:
            warnings.append("Degree not provided")

    if year_range := rules.get("year_of_study"):
        if profile.year_of_study is not None:
            lo = year_range.get("min", 1)
            hi = year_range.get("max", 10)
            if lo <= profile.year_of_study <= hi:
                passed.append(f"Year {profile.year_of_study} within range {lo}-{hi}")
                score_factors.append(1.0)
            else:
                failed.append(f"Year of study must be {lo}-{hi}")

    eligible = len(failed) == 0
    score = sum(score_factors) / max(len(score_factors), 1) if score_factors else 0.0

    return {
        "eligible": eligible,
        "score": round(score, 2),
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
    }
