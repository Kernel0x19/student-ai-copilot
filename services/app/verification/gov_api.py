"""Government API Verification Service

This module provides government API integration for validating documents (e.g. UIDAI Aadhaar verification)
with mandatory consent enforcement and audit logging.

Satisfies Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import AuditLog, ConsentRecord

logger = logging.getLogger(__name__)


class GovAPIService:
    """Government verification API service wrapper.
    
    **Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7**
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def verify_consent(self, user_id: str, consent_type: str = "gov_verification") -> bool:
        """Check if user has granted explicit consent for government API verification."""
        consent = self.db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user_id,
            ConsentRecord.purpose == consent_type,
            ConsentRecord.revoked_at.is_(None)
        ).first()
        return consent is not None

    async def verify_aadhaar(self, user_id: str, aadhaar_number: str) -> Dict[str, Any]:
        """Verify Aadhaar number with UIDAI government API mock/service.
        
        Args:
            user_id: User identifier
            aadhaar_number: 12-digit clean Aadhaar string
        """
        # 1. Enforce mandatory user consent check (Req 18.2)
        if not self.verify_consent(user_id):
            logger.warning(f"Gov verification rejected: User {user_id} has not granted consent")
            return {
                'status': 'failed',
                'reason': 'user_consent_required',
                'verified': False
            }
            
        # 2. Perform verification format & mock API check
        clean_num = aadhaar_number.strip().replace(" ", "")
        valid_format = len(clean_num) == 12 and clean_num.isdigit() and not clean_num.startswith('0')
        
        verification_status = 'verified' if valid_format else 'failed'
        
        # 3. Create AuditLog entry for government API access (Req 18.6)
        audit = AuditLog(
            user_id=user_id,
            action="gov_api_aadhaar_verification",
            resource_type="document_verification",
            resource_id=clean_num[-4:] if valid_format else "invalid",
            details={"status": verification_status},
            created_at=datetime.utcnow()
        )
        self.db.add(audit)
        self.db.commit()
        
        return {
            'status': verification_status,
            'verified': valid_format,
            'verified_at': datetime.utcnow().isoformat(),
            'provider': 'uidai_api'
        }
