from app.db.session import SessionLocal
from app.db.models import StudentProfile, Opportunity, OpportunityCategory
from app.intelligence.eligibility import evaluate_eligibility
from app.intelligence.recommendation import compute_match_score
from app.agents.internship import InternshipAgent

db = SessionLocal()
profile = db.query(StudentProfile).first()
print(f"Profile: stream={profile.stream}, year={profile.year_of_study}, skills={profile.skills}")
print()

WEIGHTS = {"eligibility": 0.55, "deadline_urgency": 0.15, "profile_completeness": 0.15, "preference_match": 0.15}

print("=== SCORES PER PLATFORM (first 5 listings) ===")
for source in ['internshala', 'indeed', 'naukri', 'wellfound', 'unstop']:
    opps = db.query(Opportunity).filter_by(category=OpportunityCategory.INTERNSHIP, source=source, is_active=True).limit(5).all()
    scores = []
    for o in opps:
        score, elig, _ = compute_match_score(profile, o)
        scores.append(score)
    if scores:
        avg = sum(scores)/len(scores)
        print(f"  {source:12s}: avg={avg:.1f}  scores={[round(s,1) for s in scores]}")

print()
print("=== AGENT recommend() RESULT (limit=30) ===")
agent = InternshipAgent()
result = agent.recommend(db, profile=profile, limit=30)
by_src = {}
for m in result.matches:
    by_src[m.opportunity.source] = by_src.get(m.opportunity.source, 0) + 1
for s, c in sorted(by_src.items()):
    print(f"  {s:12s}: {c}")
print(f"  {'TOTAL':12s}: {len(result.matches)}")
db.close()
