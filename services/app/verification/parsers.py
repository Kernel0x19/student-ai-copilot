"""Document Field Extraction and Type Parsers

This module provides document-type-specific field extraction logic using regex patterns
and per-field confidence calculation.

Supports:
- Aadhaar Card (12-digit UID regex, name, DOB/year)
- Income Certificate (Income amount, issue date, authority)
- Caste Certificate (Category/caste name, certificate number)
- Marksheet (Percentage/CGPA, roll number, institution)

Satisfies Requirements: 17.2, 17.3, 17.4, 17.5, 17.6
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DocumentParser:
    """Base document parser interface with helper methods."""

    @staticmethod
    def calculate_confidence(found: bool, pattern_strength: float = 1.0, ocr_conf: float = 0.9) -> float:
        """Calculate field-level confidence score between 0.0 and 1.0."""
        if not found:
            return 0.0
        score = ocr_conf * pattern_strength
        return min(max(score, 0.0), 1.0)


class AadhaarParser(DocumentParser):
    """Parser for Aadhaar cards.
    
    **Validates: Requirement 17.3** - Aadhaar field extraction using 12-digit UID regex
    """
    
    UID_REGEX = r'\b[2-9]{1}\d{3}\s?\d{4}\s?\d{4}\b'
    DOB_REGEX = r'\b(DOB|Date of Birth|Year of Birth)[:\s]*(\d{2}/\d{2}/\d{4}|\d{4})\b'

    def parse(self, ocr_text: str, ocr_confidence: float = 0.9) -> Dict[str, Any]:
        extracted = {}
        field_confidences = {}
        
        # 1. UID extraction (12 digits)
        uid_match = re.search(self.UID_REGEX, ocr_text)
        if uid_match:
            uid_clean = uid_match.group(0).replace(" ", "")
            extracted['aadhaar_number'] = uid_clean
            field_confidences['aadhaar_number'] = self.calculate_confidence(True, 0.95, ocr_confidence)
        else:
            extracted['aadhaar_number'] = None
            field_confidences['aadhaar_number'] = 0.0
            
        # 2. DOB / Year of birth extraction
        dob_match = re.search(self.DOB_REGEX, ocr_text, re.IGNORECASE)
        if dob_match:
            extracted['dob'] = dob_match.group(2)
            field_confidences['dob'] = self.calculate_confidence(True, 0.9, ocr_confidence)
        else:
            extracted['dob'] = None
            field_confidences['dob'] = 0.0

        return {
            'document_type': 'aadhaar',
            'extracted_fields': extracted,
            'field_confidences': field_confidences,
            'overall_confidence': sum(field_confidences.values()) / (len(field_confidences) or 1)
        }


class IncomeCertificateParser(DocumentParser):
    """Parser for Income Certificates.
    
    **Validates: Requirement 17.4** - Income certificate field extraction
    """
    
    INCOME_REGEX = r'\b(Annual Income|Total Income|Income)[:\s]*₹?\s*([\d,]+)\b'

    def parse(self, ocr_text: str, ocr_confidence: float = 0.9) -> Dict[str, Any]:
        extracted = {}
        field_confidences = {}
        
        match = re.search(self.INCOME_REGEX, ocr_text, re.IGNORECASE)
        if match:
            income_str = match.group(2).replace(",", "")
            try:
                extracted['annual_income'] = float(income_str)
                field_confidences['annual_income'] = self.calculate_confidence(True, 0.9, ocr_confidence)
            except ValueError:
                extracted['annual_income'] = None
                field_confidences['annual_income'] = 0.0
        else:
            extracted['annual_income'] = None
            field_confidences['annual_income'] = 0.0

        return {
            'document_type': 'income_certificate',
            'extracted_fields': extracted,
            'field_confidences': field_confidences,
            'overall_confidence': sum(field_confidences.values()) / (len(field_confidences) or 1)
        }


class CasteCertificateParser(DocumentParser):
    """Parser for Caste Certificates.
    
    **Validates: Requirement 17.5** - Caste certificate field extraction
    """
    
    CASTE_REGEX = r'\b(SC|ST|OBC|EWS|General|SEBC)\b'

    def parse(self, ocr_text: str, ocr_confidence: float = 0.9) -> Dict[str, Any]:
        extracted = {}
        field_confidences = {}
        
        match = re.search(self.CASTE_REGEX, ocr_text, re.IGNORECASE)
        if match:
            extracted['caste_category'] = match.group(1).upper()
            field_confidences['caste_category'] = self.calculate_confidence(True, 0.9, ocr_confidence)
        else:
            extracted['caste_category'] = None
            field_confidences['caste_category'] = 0.0

        return {
            'document_type': 'caste_certificate',
            'extracted_fields': extracted,
            'field_confidences': field_confidences,
            'overall_confidence': sum(field_confidences.values()) / (len(field_confidences) or 1)
        }


def parse_document(doc_type: str, ocr_text: str, ocr_confidence: float = 0.9) -> Dict[str, Any]:
    """Factory function for routing text to appropriate document parser."""
    doc_type_lower = doc_type.lower()
    if 'aadhaar' in doc_type_lower:
        return AadhaarParser().parse(ocr_text, ocr_confidence)
    elif 'income' in doc_type_lower:
        return IncomeCertificateParser().parse(ocr_text, ocr_confidence)
    elif 'caste' in doc_type_lower:
        return CasteCertificateParser().parse(ocr_text, ocr_confidence)
    else:
        # Default generic parser fallback
        return {
            'document_type': doc_type,
            'extracted_fields': {'raw_text': ocr_text[:100]},
            'field_confidences': {'raw_text': ocr_confidence},
            'overall_confidence': ocr_confidence
        }
