"""Vector Similarity Search Service

This module provides semantic vector search over opportunities using cosine distance,
top-K retrieval, and eligibility/category filter combining.

Satisfies Requirements: 15.4, 15.5, 15.6, 15.7
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session

from app.db.models import Opportunity, OpportunityCategory
from app.intelligence.embeddings import EmbeddingService
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class VectorSearchService:
    """Vector similarity search provider for natural language opportunity search.
    
    **Validates: Requirements 15.4, 15.5, 15.6, 15.7**
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.embedding_service = EmbeddingService()

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two 1D vectors."""
        a = np.array(vec1)
        b = np.array(vec2)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    async def search_opportunities(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 20,
        min_score: float = 0.30,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Perform semantic search for opportunities matching natural language query.
        
        Args:
            query: Natural language search string (e.g. "engineering scholarship for low income students")
            category: Optional filter by category (e.g. "scholarship", "internship")
            top_k: Max number of top matches to return (default: 20)
            min_score: Minimum similarity score threshold (0.0 to 1.0)
            active_only: Filter out expired opportunities if True
        """
        if not query or not query.strip():
            return []
            
        query_vec = self.embedding_service.generate_embedding(query)
        
        # Query opportunities from DB
        q = self.db.query(Opportunity)
        if category:
            try:
                q = q.filter(Opportunity.category == OpportunityCategory(category))
            except ValueError:
                return []
        if active_only:
            q = q.filter(
                (Opportunity.deadline.is_(None)) | (Opportunity.deadline >= datetime.utcnow())
            )
            
        opportunities = q.all()
        scored_results = []
        
        for opp in opportunities:
            # Generate or retrieve opportunity embedding
            opp_text = f"{opp.title}. {opp.description or ''}"
            opp_vec = self.embedding_service.generate_embedding(opp_text)
            
            sim_score = self.cosine_similarity(query_vec, opp_vec)
            
            if sim_score >= min_score:
                scored_results.append({
                    'opportunity_id': opp.id,
                    'title': opp.title,
                    'description': opp.description,
                    'category': opp.category,
                    'amount': opp.amount_max or opp.amount_min,
                    'deadline': opp.deadline.isoformat() if opp.deadline else None,
                    'relevance_score': round(sim_score, 4),
                    'source_url': getattr(opp, 'source_url', None)
                })
                
        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top-K matches
        return scored_results[:top_k]

# ---------------------------------------------------------------------------
# Compatibility wrapper
# ---------------------------------------------------------------------------
# The chatbot agent imports `search_opportunities` directly from this module:
# ``from app.intelligence.vector_search import search_opportunities``.
# Previously only the ``VectorSearchService`` class defined a method with that
# name, so the import failed with ``ImportError``.  We expose a top‑level async
# function that creates a DB session, instantiates the service, and forwards the
# call.  This keeps the original class‑based implementation while providing the
# simple functional API expected by the rest of the codebase.

async def search_opportunities(
    query: str,
    category: Optional[str] = None,
    top_k: int = 20,
    min_score: float = 0.30,
    active_only: bool = True,
) -> List[Dict[str, Any]]:
    """Convenient wrapper used by the chatbot.

    It creates a short‑lived SQLAlchemy session, runs the vector‑search
    service, and closes the session before returning the results.
    """
    # Create a fresh session for this request
    db = SessionLocal()
    try:
        service = VectorSearchService(db)
        return await service.search_opportunities(
            query=query,
            category=category,
            top_k=top_k,
            min_score=min_score,
            active_only=active_only,
        )
    finally:
        db.close()
