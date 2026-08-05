from app.db.session import SessionLocal, init_db
from app.db.models import Opportunity, OpportunityCategory
from app.ingestion.normalizer import normalize_internship, upsert_opportunity
from app.knowledge.hybrid_rag import HybridRAG
from app.ingestion.connectors.indeed_connector import IndeedConnector
from app.ingestion.connectors.naukri_connector import NaukriConnector
from app.ingestion.connectors.wellfound_connector import WellfoundConnector
from app.ingestion.connectors.unstop_connector import UnstopConnector
from app.ingestion.connectors.seed_connectors import InternshalaSeeder

init_db()
db = SessionLocal()
rag = HybridRAG()

for ConnClass in [IndeedConnector, NaukriConnector, WellfoundConnector, UnstopConnector, InternshalaSeeder]:
    c = ConnClass()
    items = c.fetch()
    for raw in items:
        data = normalize_internship(raw)
        opp = upsert_opportunity(db, data)
        opp.is_active = True
        db.flush()
        rag.index_opportunity(opp)
    db.commit()
    print(f"{c.source_id}: {len(items)} listings reseeded")

by_source = {}
for r in db.query(Opportunity).filter_by(category=OpportunityCategory.INTERNSHIP, is_active=True).all():
    by_source[r.source] = by_source.get(r.source, 0) + 1
print()
print("Active internships by source:")
for s, c in sorted(by_source.items()):
    print(f"  {s}: {c}")
print(f"  TOTAL: {sum(by_source.values())}")
db.close()
