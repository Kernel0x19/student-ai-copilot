"""
One-shot ingestion script: loads all 788 schemes from
app/data/student_schemes.json into the DB + ChromaDB.

Run from services/ directory:
    python eval/ingest_schemes.py
"""
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.models import Opportunity, OpportunityCategory
from app.db.session import SessionLocal
from app.knowledge.hybrid_rag import HybridRAG

SCHEMES_FILE = ROOT.parent / "app" / "data" / "student_schemes.json"


def map_category(raw: str) -> OpportunityCategory:
    """Map raw category string to OpportunityCategory enum."""
    r = (raw or "").lower()
    if "internship" in r:
        return OpportunityCategory.INTERNSHIP
    if "hackathon" in r or "competition" in r:
        return OpportunityCategory.HACKATHON
    if "placement" in r or "job" in r:
        return OpportunityCategory.PLACEMENT
    return OpportunityCategory.SCHOLARSHIP


def main():
    print(f"Loading schemes from {SCHEMES_FILE}...")
    with open(SCHEMES_FILE, encoding="utf-8") as f:
        data = json.load(f)

    schemes = data.get("schemes", [])
    print(f"Found {len(schemes)} schemes.\n")

    db = SessionLocal()
    rag = HybridRAG()

    inserted = 0
    updated = 0
    errors = 0

    try:
        for i, s in enumerate(schemes, 1):
            try:
                scheme_id = s.get("scheme_id") or str(uuid.uuid4())
                title = (s.get("title") or "").strip()[:500]
                if not title:
                    continue

                description = (
                    s.get("description")
                    or s.get("raw_text")
                    or ""
                ).strip()

                eligibility_text = (s.get("eligibility") or "").strip()
                benefits = (s.get("benefits") or "").strip()
                documents = (s.get("documents_required") or "").strip()
                # NOTE: do NOT store official_link as source_url because hundreds of schemes
                # share the same URL (scholarships.gov.in) and source_url has a unique index.
                application_url = (s.get("official_link") or "").strip() or None
                category = map_category(s.get("category", ""))

                # Build eligibility_rules dict from text
                eligibility_rules = {}
                if eligibility_text:
                    eligibility_rules["description"] = eligibility_text[:2000]

                # Combine description + benefits for richer vector indexing
                full_description = description
                if benefits:
                    full_description += f"\n\nBenefits: {benefits}"

                # Upsert by external_id
                existing = (
                    db.query(Opportunity)
                    .filter_by(source="student_schemes_json", external_id=scheme_id)
                    .first()
                )

                if existing:
                    existing.title = title
                    existing.description = full_description[:5000]
                    existing.eligibility_rules = eligibility_rules
                    existing.documents_required = [documents] if documents else []
                    existing.application_url = application_url
                    existing.is_active = True
                    opp = existing
                    updated += 1
                else:
                    opp = Opportunity(
                        id=str(uuid.uuid4()),
                        source="student_schemes_json",
                        external_id=scheme_id,
                        title=title,
                        description=full_description[:5000],
                        category=category,
                        eligibility_rules=eligibility_rules,
                        documents_required=[documents] if documents else [],
                        application_url=application_url,
                        source_url=None,  # avoid unique constraint collision
                        is_active=True,
                        tags=[s.get("ministry", ""), s.get("state", "")],
                    )
                    db.add(opp)
                    inserted += 1

                db.flush()
                rag.index_opportunity(opp)

                if i % 100 == 0:
                    db.commit()
                    print(f"  Progress: {i}/{len(schemes)} (inserted={inserted}, updated={updated}, errors={errors})")

            except Exception as e:
                errors += 1
                db.rollback()  # recover the session for next iteration
                if errors <= 5:
                    print(f"  Error on scheme {i} ({s.get('title', '')[:40]}): {e}")
                continue

        db.commit()
        print(f"\n✅ Done!")
        print(f"   Inserted : {inserted}")
        print(f"   Updated  : {updated}")
        print(f"   Errors   : {errors}")
        print(f"\nTotal active in DB now: {db.query(Opportunity).filter_by(is_active=True).count()}")

    finally:
        db.close()



if __name__ == "__main__":
    main()
