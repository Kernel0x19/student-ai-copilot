"""Document Upload and Verification API Routes

This module provides document upload, AES-256 GCM encryption, database record creation,
and document auto-verification workflow triggering endpoints.

Satisfies Requirements: 17.1, 18.1, 19.1, 19.4, 19.5
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Document, Application
from app.security.document_store import DocumentStore
from app.verification.engine import AutoVerificationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["Document Verification"])


@router.post("/upload")
async def upload_and_verify_document(
    user_id: str = Form(...),
    document_type: str = Form(...),
    application_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Upload document file, encrypt at rest, and run auto-verification pipeline."""
    if not file:
        raise HTTPException(status_code=400, detail="File payload missing")
        
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file contents")
        
    doc_id = f"doc-{uuid.uuid4().hex[:12]}"
    
    # 1. Encrypt document raw bytes at rest
    doc_store = DocumentStore(db)
    encrypted_bytes = doc_store.encrypt_document(doc_id, content)
    
    # 2. Run Auto-Verification Engine
    engine = AutoVerificationEngine(db)
    verification_res = await engine.verify_document(
        user_id=user_id,
        document_type=document_type,
        image_bytes=content,
        application_id=application_id
    )
    
    # 3. Store Document metadata entry in DB
    doc_record = Document(
        id=doc_id,
        user_id=user_id,
        document_type=document_type,
        file_path=f"/secure/documents/{doc_id}.enc",
        encryption_key_id=f"kdf-{doc_id}",
        verification_status=verification_res.get('verification_status', 'pending'),
        extracted_fields=verification_res.get('extracted_fields'),
        overall_confidence=verification_res.get('confidence_score', 0.0),
        gov_verification_status='verified' if verification_res.get('gov_api_verified') else 'not_verified',
        created_at=datetime.utcnow()
    )
    db.add(doc_record)
    db.commit()
    
    return {
        "document_id": doc_id,
        "document_type": document_type,
        "verification_status": doc_record.verification_status,
        "extracted_fields": doc_record.extracted_fields,
        "confidence_score": doc_record.overall_confidence,
        "uploaded_at": doc_record.created_at.isoformat()
    }


@router.get("/{document_id}/status")
def get_document_verification_status(
    document_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Query current verification status for uploaded document."""
    doc = db.query(Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document record not found")
        
    return {
        "document_id": doc.id,
        "document_type": doc.document_type,
        "verification_status": doc.verification_status,
        "extracted_fields": doc.extracted_fields,
        "confidence_score": doc.overall_confidence,
        "gov_verification_status": doc.gov_verification_status
    }
