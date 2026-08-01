"""Admin Connector Trigger & Status API Routes

This module provides admin endpoints to trigger data connector runs manually
and query execution status and freshness across connectors.

Satisfies Requirements: 4.6, 6.1, 6.2, 6.3, 6.4
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ingestion.connector_registry import ConnectorOrchestrator
from app.db.models import ConnectorStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/connectors", tags=["Admin Connectors"])


@router.get("/status")
def get_connector_statuses(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get latest run status and data freshness metrics for all connectors."""
    statuses = db.query(ConnectorStatus).all()
    result = []
    for st in statuses:
        result.append({
            "name": st.name,
            "last_run": st.last_run.isoformat() if st.last_run else None,
            "last_success": st.last_success.isoformat() if st.last_success else None,
            "records_processed": st.records_processed,
            "is_stale": st.is_stale,
            "last_error": st.last_error
        })
    return {"connectors": result, "count": len(result)}


@router.post("/trigger")
async def trigger_connector_run(
    connector_name: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger data connector execution."""
    from app.config import get_settings
    settings = get_settings()
    
    orchestrator = ConnectorOrchestrator(
        db, 
        config={"enabled_connectors": settings.enabled_connectors_list}
    )
    
    if connector_name:
        logger.info(f"Manually triggering single connector: {connector_name}")
        results = await orchestrator.run_connector(connector_name)
    else:
        logger.info("Manually triggering all data connectors sequentially")
        results = await orchestrator.run_all()
        
    return {
        "status": "triggered",
        "connector_name": connector_name or "all",
        "results": results
    }
