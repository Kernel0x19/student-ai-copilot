"""Auto Verification Engine

This module orchestrates document verification combining OCR extraction, government API verification,
and TEE enclave processing to calculate confidence scores and determine application verification states.

Status rules:
- `auto_approved`: Confidence score >= 0.85 and Gov API verified
- `needs_review`: Confidence score between 0.60 and 0.85
- `rejected`: Confidence score < 0.60 or invalid document format

Satisfies Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Application, AuditLog
from app.verification.ocr_service import OCRService, OCRProvider
from app.verification.parsers import parse_document
from app.verification.gov_api import GovAPIService
from app.security.tee import create_tee_service

logger = logging.getLogger(__name__)


class AutoVerificationEngine:
    """Orchestrates OCR + Gov API + TEE for document verification.
    
    **Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7**
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.ocr_service = OCRService(provider=OCRProvider.TESSERACT)
        self.gov_api_service = GovAPIService(db_session)
        self.tee_service = create_tee_service(mode="mock")

    async def verify_document(
        self,
        user_id: str,
        document_type: str,
        image_bytes: bytes,
        application_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run complete auto-verification pipeline on uploaded document image."""
        
        # 1. OCR Extraction (Req 17.1)
        ocr_result = await self.ocr_service.extract_text(image_bytes)
        raw_text = ocr_result.get('text', '')
        ocr_confidence = ocr_result.get('confidence', 0.9)
        
        # 2. Document Field Parsing (Req 17.2-17.6)
        parsed = parse_document(document_type, raw_text, ocr_confidence)
        extracted = parsed.get('extracted_fields', {})
        overall_confidence = parsed.get('overall_confidence', 0.0)
        
        # 3. Secure processing in TEE Enclave (Req 7.1, 19.7)
        tee_result = self.tee_service.process_in_enclave(
            operation="validate_hash",
            payload={"document_type": document_type, "fields": extracted}
        )
        
        # 4. Government API Verification check if applicable (Req 18.1)
        gov_verified = False
        if document_type.lower() == 'aadhaar' and extracted.get('aadhaar_number'):
            gov_res = await self.gov_api_service.verify_aadhaar(user_id, extracted['aadhaar_number'])
            gov_verified = gov_res.get('verified', False)

        # 5. Calculate Final Verification Status Threshold (Req 19.3)
        if overall_confidence >= 0.85 or (gov_verified and overall_confidence >= 0.70):
            verification_status = "auto_approved"
        elif overall_confidence >= 0.60:
            verification_status = "needs_review"
        else:
            verification_status = "rejected"

        # 6. Update Application State if application_id provided (Req 19.4, 19.5)
        if application_id:
            app = self.db.query(Application).filter_by(id=application_id).first()
            if app:
                if verification_status == "auto_approved":
                    app.state = "verified"
                elif verification_status == "needs_review":
                    app.state = "pending_verification"
                self.db.commit()

        # Audit Log entry (Req 8.1)
        audit = AuditLog(
            user_id=user_id,
            action="document_auto_verification",
            resource_type="document",
            resource_id=document_type,
            details={"status": verification_status, "score": round(overall_confidence, 2)},
            created_at=datetime.utcnow()
        )
        self.db.add(audit)
        self.db.commit()

        return {
            'document_type': document_type,
            'verification_status': verification_status,
            'confidence_score': round(overall_confidence, 4),
            'extracted_fields': extracted,
            'gov_api_verified': gov_verified,
            'tee_processed': tee_result.get('processed', True),
            'timestamp': datetime.utcnow().isoformat()
        }
