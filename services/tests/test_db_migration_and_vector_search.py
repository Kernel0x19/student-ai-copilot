"""Unit tests for Database Migration, Embeddings, and Vector Similarity Search

Validates: Requirements 14.1-14.7, 15.1-15.7, 16.1-16.7
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.intelligence.embeddings import EmbeddingService
from app.intelligence.vector_search import VectorSearchService
from app.db.migration_script import SQLiteToPostgresMigrator
from app.db.models import Opportunity, User


@pytest.fixture
def mock_db():
    return Mock()


def test_embedding_service_generation():
    service = EmbeddingService()
    vec = service.generate_embedding("Engineering Scholarship 2026")
    
    assert isinstance(vec, list)
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)


def test_embedding_service_deterministic_output():
    service = EmbeddingService()
    vec1 = service.generate_embedding("AICTE Pragati Scholarship")
    vec2 = service.generate_embedding("AICTE Pragati Scholarship")
    
    assert vec1 == vec2


@pytest.mark.asyncio
async def test_vector_search_service(mock_db):
    opp1 = Mock(spec=Opportunity)
    opp1.id = "opp-1"
    opp1.title = "Software Engineering Internship"
    opp1.description = "Full stack developer role with stipend for Computer Science students"
    opp1.category = "internship"
    opp1.amount = 25000
    opp1.deadline = datetime.utcnow() + timedelta(days=30)
    opp1.source_url = "https://example.com/opp1"

    opp2 = Mock(spec=Opportunity)
    opp2.id = "opp-2"
    opp2.title = "Arts and Music Fellowship"
    opp2.description = "Grant for fine arts and classical music research"
    opp2.category = "grant"
    opp2.amount = 50000
    opp2.deadline = datetime.utcnow() + timedelta(days=60)
    opp2.source_url = "https://example.com/opp2"

    mock_db.query.return_value.filter.return_value.all.return_value = [opp1, opp2]
    mock_db.query.return_value.all.return_value = [opp1, opp2]

    search_service = VectorSearchService(mock_db)
    
    results = await search_service.search_opportunities(
        query="software developer internship computer science",
        top_k=5,
        min_score=-1.0
    )

    assert len(results) > 0
    assert results[0]['opportunity_id'] == "opp-1"
    assert 'relevance_score' in results[0]


def test_migrator_record_counts(mock_db):
    src_session = Mock()
    tgt_session = Mock()
    
    src_session.query.return_value.scalar.return_value = 10
    tgt_session.query.return_value.scalar.return_value = 10

    migrator = SQLiteToPostgresMigrator.__new__(SQLiteToPostgresMigrator)
    counts = migrator.verify_record_counts(src_session, tgt_session)
    
    assert isinstance(counts, dict)
    assert 'users' in counts
    assert counts['users']['match'] is True
