"""Unit tests for DocumentStore Encryption at Rest

Validates: Requirements 9.1-9.7
"""

import pytest
from unittest.mock import Mock

from app.security.document_store import DocumentStore
from app.db.models import ConsentRecord, AuditLog


@pytest.fixture
def mock_db():
    return Mock()


def test_document_encryption_and_decryption_with_consent(mock_db):
    consent = Mock(spec=ConsentRecord)
    mock_db.query.return_value.filter.return_value.first.return_value = consent
    
    store = DocumentStore(mock_db)
    doc_id = "doc-999"
    original_payload = b"Sensitive income certificate document content 2026"
    
    encrypted = store.encrypt_document(doc_id, original_payload)
    assert encrypted != original_payload
    
    decrypted = store.decrypt_document("user-123", doc_id, encrypted)
    assert decrypted == original_payload
    assert mock_db.add.called  # Audit log created


def test_decryption_fails_without_consent(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    store = DocumentStore(mock_db)
    doc_id = "doc-888"
    encrypted = store.encrypt_document(doc_id, b"Secret")
    
    with pytest.raises(PermissionError, match="User consent required"):
        store.decrypt_document("user-123", doc_id, encrypted)
