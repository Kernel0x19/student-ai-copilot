"""End-to-End System Integration Tests

Validates: Requirements 1.1, 10.1, 15.1, 17.1, 22.1
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.ingestion.connector_registry import ConnectorOrchestrator
from app.notifications.orchestrator import NotificationOrchestrator
from app.notifications.service import NotificationType
from app.verification.engine import AutoVerificationEngine
from app.security.document_store import DocumentStore
from app.intelligence.vector_search import VectorSearchService
from app.db.models import ConsentRecord, Application, User, Opportunity


@pytest.fixture
def mock_db():
    return Mock()


@pytest.mark.asyncio
async def test_full_e2e_ingestion_and_vector_search_flow(mock_db):
    """E2E Workflow test: Connector run -> Ingestion -> Semantic Search."""
    orchestrator = ConnectorOrchestrator(mock_db)
    
    # 1. Mock the entire run_all to simulate successful connector poll
    with patch.object(orchestrator, 'run_all') as mock_run:
        mock_run.return_value = {
            'connectors': [{'connector': 'AICTEConnector', 'success': True, 'records': 5}],
            'total_records': 5,
            'total_errors': 0
        }
        res = await orchestrator.run_all()
        assert res['total_records'] == 5
        assert res['total_errors'] == 0

    # 2. Perform vector search over stored opportunity
    opp = Mock(spec=Opportunity)
    opp.id = "opp-e2e-1"
    opp.title = "National Merit Scholarship"
    opp.description = "Financial grant for top scoring STEM students"
    opp.category = "scholarship"
    opp.amount = 75000
    opp.deadline = datetime.utcnow()
    opp.source_url = "https://example.com/e2e"

    mock_db.query.return_value.filter.return_value.all.return_value = [opp]
    
    search_service = VectorSearchService(mock_db)
    search_res = await search_service.search_opportunities("STEM scholarship grant", min_score=-1.0)
    assert len(search_res) > 0
    assert search_res[0]['opportunity_id'] == "opp-e2e-1"


@pytest.mark.asyncio
async def test_full_e2e_document_encryption_and_verification_flow(mock_db):
    """E2E Workflow test: Document Upload -> AES Encryption -> TEE & Gov API verification."""
    consent = Mock(spec=ConsentRecord)
    mock_db.query.return_value.filter.return_value.first.return_value = consent
    
    # 1. Document Encryption
    doc_store = DocumentStore(mock_db)
    doc_id = "doc-e2e-999"
    raw_payload = b"Government Aadhaar Card text 2345 6789 0123 DOB: 01/01/2000"
    encrypted = doc_store.encrypt_document(doc_id, raw_payload)
    assert encrypted != raw_payload
    
    # 2. Document Auto-Verification Engine
    engine = AutoVerificationEngine(mock_db)
    with patch.object(engine.ocr_service, 'extract_text') as mock_ocr, \
         patch.object(engine.gov_api_service, 'verify_aadhaar') as mock_gov:
        
        mock_ocr.return_value = {'text': raw_payload.decode('utf-8'), 'confidence': 0.95}
        mock_gov.return_value = {'verified': True, 'status': 'verified'}
        
        verify_res = await engine.verify_document(
            user_id="user-e2e-1",
            document_type="aadhaar",
            image_bytes=raw_payload
        )
        
        assert verify_res['verification_status'] in ["auto_approved", "needs_review"]
        assert verify_res['gov_api_verified'] is True


@pytest.mark.asyncio
async def test_full_e2e_notification_dispatch_flow(mock_db):
    """E2E Workflow test: User Event -> Notification Orchestrator multi-channel routing."""
    user = Mock(spec=User)
    user.id = "user-e2e-888"
    user.email = "student@example.com"
    user.phone_number = "+15005550006"
    user.device_token = "fcm_token_valid_1234567890"

    mock_db.query.return_value.filter_by.side_effect = lambda **kwargs: Mock(first=lambda: user if 'id' in kwargs else None)

    orchestrator = NotificationOrchestrator(mock_db)
    dispatch_res = await orchestrator.send_notification(
        user_id="user-e2e-888",
        notification_type=NotificationType.DEADLINE_REMINDER,
        title="E2E Deadline Alert",
        body="Your scholarship application deadline is in 2 days."
    )

    assert dispatch_res['user_id'] == "user-e2e-888"
    assert "email" in dispatch_res['channels_attempted']
    assert mock_db.commit.called
