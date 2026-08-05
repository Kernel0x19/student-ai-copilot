from app.db.models import Opportunity, OpportunityCategory
from app.ingestion.base import RawOpportunity


def normalize(raw: RawOpportunity) -> dict:
    """Map raw source record to standard Opportunity fields."""
    amount_display = None
    if raw.amount_min and raw.amount_max:
        amount_display = f"₹{raw.amount_min:,.0f} – ₹{raw.amount_max:,.0f}"
    elif raw.amount_max:
        amount_display = f"Up to ₹{raw.amount_max:,.0f}"

    return {
        "external_id": raw.external_id,
        "source": raw.source,
        "category": OpportunityCategory.SCHOLARSHIP,
        "title": raw.title.strip(),
        "description": raw.description.strip(),
        "amount_min": raw.amount_min,
        "amount_max": raw.amount_max,
        "deadline": raw.deadline,
        "eligibility_rules": raw.eligibility_rules,
        "documents_required": raw.documents_required,
        "application_url": raw.application_url,
        "state_filter": raw.state_filter,
        "tags": raw.tags + ([amount_display] if amount_display else []),
        "raw_data": raw.raw_data or {"source_title": raw.title},
        "is_active": True,
    }


def normalize_internship(raw: RawOpportunity) -> dict:
    """Map raw internship record to standard Opportunity fields.

    Stipend values go into amount_min/amount_max.
    Company, location, and duration are stored in raw_data for the frontend to read.
    """
    stipend_display = None
    if raw.amount_min and raw.amount_max:
        stipend_display = f"₹{raw.amount_min:,.0f} – ₹{raw.amount_max:,.0f}/mo"
    elif raw.amount_max:
        stipend_display = f"Up to ₹{raw.amount_max:,.0f}/mo"

    extra = raw.raw_data or {}

    return {
        "external_id": raw.external_id,
        "source": raw.source,
        "category": OpportunityCategory.INTERNSHIP,
        "title": raw.title.strip(),
        "description": raw.description.strip(),
        "amount_min": raw.amount_min,
        "amount_max": raw.amount_max,
        "deadline": raw.deadline,
        "eligibility_rules": raw.eligibility_rules,
        "documents_required": raw.documents_required,
        "application_url": raw.application_url,
        "state_filter": raw.state_filter,
        "tags": raw.tags + ([stipend_display] if stipend_display else []),
        "raw_data": {
            "source_title": raw.title,
            "company": extra.get("company"),
            "location": extra.get("location"),
            "duration": extra.get("duration"),
        },
        "is_active": True,
    }


def upsert_opportunity(db, data: dict) -> Opportunity:
    existing = (
        db.query(Opportunity)
        .filter_by(source=data["source"], external_id=data["external_id"])
        .first()
    )
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.add(existing)
        return existing

    opp = Opportunity(**data)
    db.add(opp)
    return opp
