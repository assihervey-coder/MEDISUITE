"""Cas d'usage — évaluation complète d'une proposition (DECISION_PENDING)."""
from __future__ import annotations

from typing import Any


def evaluate(proposal_dict: dict[str, Any], assessment: dict[str, Any]) -> dict[str, Any]:
    """Prépare la décision : classe, risque, gates requis, recommandation."""
    klass = proposal_dict.get("change_class") or "P3"
    risk_level = assessment.get("risk", {}).get("level", "LOW")
    recommendation = "APPROVE" if risk_level in ("LOW", "MEDIUM") else "REVIEW_COMMITTEE"
    if klass in ("P8", "P9"):
        recommendation = "REVIEW_COMMITTEE"
    return {
        "proposal_id": proposal_dict.get("id"),
        "change_class": klass,
        "risk_level": risk_level,
        "blast_radius": assessment.get("blast_radius", {}).get("level"),
        "gates_required": assessment.get("risk", {}).get("required_gates", []),
        "recommendation": recommendation,
    }
