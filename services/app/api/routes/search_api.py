"""Semantic Vector Search API Routes

This module provides natural language opportunity search endpoints backed by pgvector similarity matching.

Satisfies Requirements: 15.1, 15.5, 15.6, 15.7
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.intelligence.vector_search import VectorSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["Semantic Search"])


@router.get("/opportunities")
async def search_opportunities_semantic(
    q: str = Query(..., min_length=1, description="Natural language search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    top_k: int = Query(20, ge=1, le=100, description="Max results"),
    min_score: float = Query(0.10, ge=-1.0, le=1.0, description="Minimum relevance score"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Execute semantic vector similarity search over opportunities."""
    search_service = VectorSearchService(db)
    results = await search_service.search_opportunities(
        query=q,
        category=category,
        top_k=top_k,
        min_score=min_score
    )
    return {
        "query": q,
        "category": category,
        "results_count": len(results),
        "matches": results
    }
