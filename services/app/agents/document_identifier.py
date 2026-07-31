"""Classify OCR text into the supported student-document types.

The local Ollama call is deliberately best-effort: document intake must still work
when a developer has not started Ollama, so high-signal document markers provide a
deterministic fallback.
"""

import json
import re
from typing import Any

from app.config import get_settings


DOCUMENT_TYPES = {
    "aadhaar": "Aadhaar Card",
    "pan": "PAN Card",
    "income_certificate": "Income Certificate",
    "caste_certificate": "Caste Certificate",
    "marksheet": "Marksheet",
    "domicile_certificate": "Domicile Certificate",
    "bank_passbook": "Bank Passbook",
    "other": "Other Document",
}


class DocumentIdentifier:
    """Uses local Ollama when available, then validates its small JSON response."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def _heuristic(text: str) -> dict[str, Any]:
        normalized = text.lower()
        markers = (
            ("aadhaar", ("aadhaar", "uidai", "unique identification")),
            ("pan", ("permanent account number", "income tax department", "pan card")),
            ("income_certificate", ("income certificate", "annual income", "total income")),
            ("caste_certificate", ("caste certificate", "scheduled caste", "scheduled tribe", "other backward")),
            ("marksheet", ("marksheet", "mark sheet", "semester", "cgpa", "grade point")),
            ("domicile_certificate", ("domicile certificate", "residence certificate", "permanent resident")),
            ("bank_passbook", ("passbook", "account number", "ifsc")),
        )
        for doc_type, keywords in markers:
            if any(keyword in normalized for keyword in keywords):
                return {"document_type": doc_type, "confidence": 0.85, "method": "heuristic"}
        return {"document_type": "other", "confidence": 0.35, "method": "heuristic"}

    async def identify(self, ocr_text: str) -> dict[str, Any]:
        """Return a supported document type and a confidence in the 0-1 range."""
        fallback = self._heuristic(ocr_text)
        if not ocr_text.strip():
            return fallback
        try:
            from langchain_ollama import ChatOllama

            prompt = (
                "Classify this Indian student document. Choose exactly one type from "
                f"{', '.join(DOCUMENT_TYPES)}. Return JSON only: "
                '{"document_type":"type", "confidence":0.0}. OCR text:\n'
                f"{ocr_text[:4000]}"
            )
            response = await ChatOllama(
                model=self.settings.ollama_model,
                temperature=0,
                base_url=self.settings.ollama_base_url,
            ).ainvoke(prompt)
            match = re.search(r"\{.*?\}", str(response.content), re.DOTALL)
            parsed = json.loads(match.group(0)) if match else {}
            doc_type = parsed.get("document_type")
            confidence = float(parsed.get("confidence", 0))
            if doc_type in DOCUMENT_TYPES and 0 <= confidence <= 1:
                return {"document_type": doc_type, "confidence": confidence, "method": "ollama"}
        except Exception:
            # Local classification is optional; raw OCR is never returned to callers.
            pass
        return fallback

