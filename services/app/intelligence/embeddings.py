"""Sentence Embedding Service for Semantic Vector Search

This module provides vector embedding generation using SentenceTransformer models (384 dimensions)
for opportunity title and description fields with a deterministic mock fallback.

Satisfies Requirements: 15.1, 15.2, 15.3
"""

import hashlib
import logging
import re
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates 384-dimensional dense vector embeddings for semantic search.
    
    **Validates: Requirements 15.1, 15.2, 15.3**
    """
    
    VECTOR_DIM = 384

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Attempt to load SentenceTransformer model with fallback handling."""
        import os
        if os.environ.get("USE_REAL_TRANSFORMERS", "").lower() != "true":
            logger.info("Using deterministic vector generator for embeddings (USE_REAL_TRANSFORMERS not set).")
            self.model = None
            return
            
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, local_files_only=True)
            logger.info(f"Loaded SentenceTransformer model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to deterministic vector generator.")
            self.model = None

    def generate_embedding(self, text: str) -> List[float]:
        """Generate 384-dim normalized floating point vector embedding for text.
        
        Args:
            text: Input text string (title + description)
            
        Returns:
            List of 384 floats representing normalized embedding vector.
        """
        if not text:
            return [0.0] * self.VECTOR_DIM
            
        if self.model is not None:
            embedding = self.model.encode(text, convert_to_numpy=True)
            # Normalize vector to unit length
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            return embedding.tolist()
        else:
            # Offline fallback: feature hashing preserves overlap between a query
            # and an opportunity. The former full-text random vector made every
            # result effectively random when no local transformer model was present.
            tokens = re.findall(r"[\w\u0900-\u097f]+", text.lower())
            aliases = {
                "engineering": ("technical",), "technical": ("engineering",),
                "girls": ("women", "female"), "girl": ("women", "female"),
                "women": ("girls", "female"), "maharashtra": ("mh",),
                "scholarship": ("grant", "stipend"), "internship": ("training",),
            }
            features = list(tokens)
            for token in tokens:
                features.extend(aliases.get(token, ()))
            # Include adjacent pairs so phrases such as "income certificate"
            # and "professional course" rank more precisely.
            features.extend(f"{tokens[i]}_{tokens[i + 1]}" for i in range(len(tokens) - 1))
            vec = np.zeros(self.VECTOR_DIM, dtype=float)
            for feature in features:
                digest = hashlib.sha256(feature.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.VECTOR_DIM
                vec[index] += 1.0 if digest[4] % 2 else -1.0
            norm = np.linalg.norm(vec)
            return (vec / norm).tolist() if norm else vec.tolist()

    def generate_opportunity_embedding(self, title: str, description: str, category: Optional[str] = None) -> List[float]:
        """Generate combined vector embedding for opportunity metadata."""
        full_text = f"{title}. {description or ''}"
        if category:
            full_text += f" Category: {category}"
        return self.generate_embedding(full_text)

# ---------------------------------------------------------------------------
# Helper for backward‑compatible import
# ---------------------------------------------------------------------------
def get_embedding_model() -> EmbeddingService:
    """Return a ready‑to‑use :class:`EmbeddingService` instance.

    The original chatbot code expected a function ``get_embedding_model`` to be
    imported from ``app.intelligence.embeddings``.  Providing this thin wrapper
    keeps the public API stable without altering the existing ``EmbeddingService``
    implementation.
    """
    return EmbeddingService()
