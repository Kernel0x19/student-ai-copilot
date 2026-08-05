from app.db.session import SessionLocal
from app.db.models import StudentProfile, Opportunity, OpportunityCategory
from app.intelligence.eligibility import evaluate_eligibility
from app.intelligence.recommendation import compute_match_score, _deadline_score, _profile_completeness, _preference_match

db = SessionLocal()
profile = db.query(StudentProfile).first()
print(f"Profile stream={profile.stream} skills={profile.skills} year={profile.year_of_study}")
print()

WEIGHTS = {"eligibility": 0.55, "deadline_urgency": 0.15, "profile_completeness": 0.15, "preference_match": 0.15}

for source in ['internshala', 'naukri', 'wellfound', 'unstop', 'indeed']:
    opps = db.query(Opportunity).filter_by(
        category=OpportunityCategory.INTERNSHIP,
        source=source,
        is_active=True
    ).limit(3).all()
    print(f"=== {source.upper()} ===")
    for o in opps:
        elig = evaluate_eligibility(profile, o.eligibility_rules or {})
        dl   = _deadline_score(o)
        comp = _profile_completeness(profile)
        pref = _preference_match(profile, o)
        final = (WEIGHTS['eligibility']*elig['score'] + WEIGHTS['deadline_urgency']*dl +
                 WEIGHTS['profile_completeness']*comp + WEIGHTS['preference_match']*pref) * 100
        print(f"  {o.title[:45]}")
        print(f"    rules={o.eligibility_rules}")
        print(f"    elig_score={elig['score']} eligible={elig['eligible']}")
        print(f"    passed={elig['passed']} failed={elig['failed']}")
        print(f"    dl={dl:.2f} comp={comp:.2f} pref={pref:.2f}")
        print(f"    FINAL={final:.1f}")
    print()

db.close()
