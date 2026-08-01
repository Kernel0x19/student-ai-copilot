import hashlib
import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.db.models import Opportunity, StudentProfile
from app.intelligence.eligibility import evaluate_eligibility

logger = logging.getLogger(__name__)
settings = get_settings()


class HybridRAG:
    """Structured DB (SQLAlchemy) + ChromaDB vector store for semantic search."""

    COLLECTION = "opportunities"

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def _doc_text(self, opp: Opportunity) -> str:
        parts = [opp.title, opp.description or ""]
        if opp.eligibility_rules:
            parts.append(str(opp.eligibility_rules))
        if opp.tags:
            parts.append(" ".join(opp.tags))
        return " ".join(parts)

    def _embedding_id(self, opp: Opportunity) -> str:
        return hashlib.sha256(f"{opp.source}:{opp.external_id}".encode()).hexdigest()[:32]

    def index_opportunity(self, opp: Opportunity) -> str:
        doc_id = self._embedding_id(opp)
        text = self._doc_text(opp)
        self._collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[
                {
                    "opportunity_id": opp.id,
                    "source": opp.source,
                    "category": opp.category.value if opp.category else "scholarship",
                    "title": opp.title[:200],
                }
            ],
        )
        opp.embedding_id = doc_id
        return doc_id

    def semantic_search(self, query: str, limit: int = 20, category: str | None = None) -> list[dict[str, Any]]:
        where = {"category": category} if category else None
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=limit,
                where=where,
            )
        except Exception:
            results = self._collection.query(query_texts=[query], n_results=limit)

        items = []
        if results and results.get("ids") and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0.0
                items.append(
                    {
                        "embedding_id": doc_id,
                        "opportunity_id": meta.get("opportunity_id"),
                        "score": max(0.0, 1.0 - distance),
                        "title": meta.get("title"),
                    }
                )
        return items

    def reindex_all(self, db) -> int:
        count = 0
        for opp in db.query(Opportunity).filter_by(is_active=True).all():
            self.index_opportunity(opp)
            count += 1
        db.commit()
        return count

    def retrieve_for_profile(self, db, query: str, profile: StudentProfile | None, limit: int = 5) -> list[dict[str, Any]]:
        """Retrieve semantically relevant opportunities, then retain eligible matches.

        Eligibility is applied before the chat model sees any schemes so it cannot
        present a good semantic match as a recommendation for an ineligible user.
        """
        candidates = self.semantic_search(query, limit=max(limit * 4, 20), category="scholarship")
        ids = [item["opportunity_id"] for item in candidates if item.get("opportunity_id")]
        opportunities = {
            opp.id: opp for opp in db.query(Opportunity).filter(
                Opportunity.id.in_(ids), Opportunity.is_active.is_(True)
            ).all()
        } if ids else {}
        ranked: list[dict[str, Any]] = []
        for candidate in candidates:
            opportunity = opportunities.get(candidate.get("opportunity_id"))
            if not opportunity:
                continue
            eligibility = evaluate_eligibility(profile, opportunity.eligibility_rules or {})
            if not eligibility["eligible"]:
                continue
            ranked.append({
                "opportunity_id": opportunity.id,
                "title": opportunity.title,
                "description": opportunity.description or "",
                "category": opportunity.category.value if opportunity.category else "scholarship",
                "relevance_score": candidate["score"],
                "eligibility_score": eligibility["score"],
                "eligibility": eligibility,
                "deadline": opportunity.deadline.isoformat() if opportunity.deadline else None,
                "amount": opportunity.amount_max or opportunity.amount_min,
                "source_url": opportunity.application_url or opportunity.source_url,
            })
        ranked.sort(key=lambda item: (item["eligibility_score"], item["relevance_score"]), reverse=True)
        return ranked[:limit]
