"""Adapter Med42 — normalise les sorties vers le modèle de domaine."""
from __future__ import annotations

from tropirag.ai.text.med42.client import Med42Client  # noqa: F401


def parse_synthesis(structured: dict | None) -> dict:
    """Normalise la sortie JSON Med42 en structure contrôlée."""
    if not isinstance(structured, dict):
        return {"summary": "", "key_findings": [], "differential_review": [],
                "warnings": [], "citations": [], "parse_ok": False}
    return {
        "summary": str(structured.get("summary", "")),
        "key_findings": [str(x) for x in structured.get("key_findings", [])],
        "differential_review": [str(x) for x in structured.get("differential_review", [])],
        "warnings": [str(x) for x in structured.get("warnings", [])],
        "citations": [str(c) for c in structured.get("citations", [])],
        "parse_ok": True,
    }
