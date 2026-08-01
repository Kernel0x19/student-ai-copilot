import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Opportunity
from app.ingestion.normalizer import normalize, upsert_opportunity
from app.knowledge.hybrid_rag import HybridRAG

logger = logging.getLogger(__name__)

# Import available connectors
CONNECTORS = []
try:
    from app.ingestion.connectors import NSPConnector, MahaDBTConnector, MySchemeConnector
    CONNECTORS = [NSPConnector(), MahaDBTConnector(), MySchemeConnector()]
except ImportError:
    # Connectors not yet implemented - log warning
    logger.warning("Data source connectors not yet implemented")
    CONNECTORS = []


def run_ingestion(db: Session) -> dict:
    """Run all MVP scholarship connectors and sync to DB + vector store."""
    rag = HybridRAG()
    stats = {"inserted": 0, "updated": 0, "errors": 0, "sources": {}}

    for connector in CONNECTORS:
        source_stats = {"fetched": 0, "synced": 0}
        try:
            raw_items = connector.fetch()
            source_stats["fetched"] = len(raw_items)

            for raw in raw_items:
                data = normalize(raw)
                existing = (
                    db.query(Opportunity)
                    .filter_by(source=data["source"], external_id=data["external_id"])
                    .first()
                )
                opp = upsert_opportunity(db, data)
                db.flush()
                rag.index_opportunity(opp)
                if existing:
                    stats["updated"] += 1
                else:
                    stats["inserted"] += 1
                source_stats["synced"] += 1

            db.commit()
            stats["sources"][connector.source_id] = source_stats
        except Exception as exc:
            logger.exception("Ingestion failed for %s", connector.source_id)
            stats["errors"] += 1
            stats["sources"][connector.source_id] = {"error": str(exc)}
            db.rollback()

    stats["completed_at"] = datetime.utcnow().isoformat()
    return stats
