"""Confidentialité — PII et pseudonymisation."""
from __future__ import annotations

import re

_PATTERNS = {
    "phone": re.compile(r"\b(?:\+?\d{2,3}[\s.-]?){3,4}\b"),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "nir": re.compile(r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\b"),
}


def redact_pii(text: str) -> str:
    out = text
    out = _PATTERNS["email"].sub("[EMAIL]", out)
    out = _PATTERNS["phone"].sub("[TEL]", out)
    out = _PATTERNS["nir"].sub("[ID]", out)
    return out


def pseudonymize_case_id(case_id: str) -> str:
    import hashlib

    return "CASE-" + hashlib.sha256(case_id.encode()).hexdigest()[:10]
