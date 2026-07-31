"""Unit tests for Document Parsers and Auto Verification Engine

Validates: Requirements 17.2-17.6, 18.1-18.7, 19.1-19.7
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.verification.parsers import AadhaarParser, IncomeCertificateParser, CasteCertificateParser, parse_document
from app.verification.gov_api import GovAPIService
from app.verification.engine import AutoVerificationEngine
from app.db.models import ConsentRecord, Application, AuditLog


@pytest.fixture
def mock_db():
    return Mock()


def test_aadhaar_parser():
    parser = AadhaarParser()
    text = "Government of India\nAadhaar No: 2345 6789 0123\nDOB: 15/08/2000"
    res = parser.parse(text, ocr_confidence=0.95)
    
    assert res['extracted_fields']['aadhaar_number'] == "234567890123"
    assert res['extracted_fields']['dob'] == "15/08/2000"
    assert res['overall_confidence'] > 0.8


def test_income_certificate_parser():
    parser = IncomeCertificateParser()
    text = "Annual Income: ₹ 150,000"
    res = parser.parse(text, ocr_confidence=0.90)
    
    assert res['extracted_fields']['annual_income'] == 150000.0
    assert res['overall_confidence'] > 0.8


def test_caste_certificate_parser():
    parser = CasteCertificateParser()
    text = "Certified that applicant belongs to OBC category"
    res = parser.parse(text, ocr_confidence=0.90)
    
    assert res['extracted_fields']['caste_category'] == "OBC"
    assert res['overall_confidence'] > 0.8


@pytest.mark.asyncio
async def test_gov_api_service_with_consent(mock_db):
    consent = Mock(spec=ConsentRecord)
    mock_db.query.return_value.filter.return_value.first.return_value = consent
    
    service = GovAPIService(mock_db)
    res = await service.verify_aadhaar("user-123", "234567890123")
    
    assert res['status'] == "verified"
    assert res['verified'] is True
    assert mock_db.add.called


@pytest.mark.asyncio
async def test_gov_api_service_without_consent(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    service = GovAPIService(mock_db)
    res = await service.verify_aadhaar("user-123", "234567890123")
    
    assert res['status'] == "failed"
    assert res['reason'] == "user_consent_required"


@pytest.mark.asyncio
async def test_auto_verification_engine(mock_db):
    app = Mock(spec=Application)
    app.id = "app-100"
    app.state = "draft"
    
    mock_db.query.return_value.filter_by.return_value.first.return_value = app
    
    engine = AutoVerificationEngine(mock_db)
    
    # Mock OCR and Gov API response
    with patch.object(engine.ocr_service, 'extract_text') as mock_ocr, \
         patch.object(engine.gov_api_service, 'verify_aadhaar') as mock_gov:
        
        mock_ocr.return_value = {
            'text': "Aadhaar Card: 2345 6789 0123\nDOB: 15/08/2000",
            'confidence': 0.95
        }
        mock_gov.return_value = {'verified': True, 'status': 'verified'}
        
        res = await engine.verify_document(
            user_id="user-123",
            document_type="aadhaar",
            image_bytes=b"fake_image_data",
            application_id="app-100"
        )
        
        assert res['verification_status'] in ["auto_approved", "needs_review"]
        assert res['gov_api_verified'] is True
        assert app.state in ["verified", "pending_verification"]
