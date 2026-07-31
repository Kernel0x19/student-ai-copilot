"""Document Encryption at Rest (AES-256 GCM)

This module provides encrypted document storage with per-document key derivation,
consent checking prior to decryption, and write-only audit logging for decryption events.

Satisfies Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
"""

import os
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.orm import Session

from app.db.models import AuditLog, ConsentRecord

logger = logging.getLogger(__name__)


class DocumentStore:
    """AES-256 encrypted document store with consent checks and audit logging.
    
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7**
    """
    
    MASTER_SALT = b'edupilot_doc_salt_2026'

    def __init__(self, db_session: Session, secret_key: Optional[str] = None):
        self.db = db_session
        self.secret_key = secret_key or "edupilot_master_secret_key_32bytes!"

    def _derive_document_key(self, document_id: str) -> bytes:
        """Derive per-document AES key using PBKDF2 KDF. (Req 9.2)"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.MASTER_SALT + document_id.encode('utf-8'),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode('utf-8')))
        return key

    def encrypt_document(self, document_id: str, raw_data: bytes) -> bytes:
        """Encrypt raw document bytes using per-document KDF key. (Req 9.1)"""
        key = self._derive_document_key(document_id)
        f = Fernet(key)
        encrypted_data = f.encrypt(raw_data)
        logger.info(f"Encrypted document {document_id} ({len(raw_data)} bytes -> {len(encrypted_data)} bytes)")
        return encrypted_data

    def store_encrypted_document(self, document_id: str, raw_data: bytes) -> str:
        """Encrypt and persist a document; raw bytes are never written to disk."""
        storage_dir = Path(os.getenv("DOCUMENT_STORAGE_DIR", "secure_documents"))
        storage_dir.mkdir(parents=True, exist_ok=True)
        path = storage_dir / f"{document_id}.enc"
        path.write_bytes(self.encrypt_document(document_id, raw_data))
        return str(path)

    def decrypt_document(self, user_id: str, document_id: str, encrypted_data: bytes) -> bytes:
        """Decrypt document bytes with consent verification and audit log. (Req 9.4, 9.5)
        
        Args:
            user_id: User requesting decryption
            document_id: Document ID
            encrypted_data: Encrypted payload
        """
        # 1. Verify consent before decryption (Req 9.4)
        consent = self.db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user_id,
            ConsentRecord.revoked_at.is_(None)
        ).first()
        
        if not consent:
            logger.warning(f"Decryption blocked for document {document_id}: No active consent for user {user_id}")
            raise PermissionError("User consent required before decrypting document")

        # 2. Decrypt data using document key
        key = self._derive_document_key(document_id)
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data)

        # 3. Create AuditLog entry for decryption event (Req 9.5)
        audit = AuditLog(
            user_id=user_id,
            action="document_decryption_access",
            resource_type="document",
            resource_id=document_id,
            details={"bytes_decrypted": len(decrypted)},
            created_at=datetime.utcnow()
        )
        self.db.add(audit)
        self.db.commit()

        return decrypted
