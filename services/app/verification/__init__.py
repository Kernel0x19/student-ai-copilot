"""Document verification system with OCR and government API integration"""

from .ocr_service import (
    OCRService,
    OCRProvider,
    create_ocr_service
)

__all__ = [
    'OCRService',
    'OCRProvider',
    'create_ocr_service',
]
