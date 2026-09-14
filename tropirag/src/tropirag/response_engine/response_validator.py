"""Validation finale de structure de la réponse avant émission."""
from __future__ import annotations

from tropirag.response_engine.clinical_response_builder import ClinicalResponse


def validate_response(r: ClinicalResponse) -> list[str]:
    issues: list[str] = []
    if not r.disclaimer:
        issues.append("disclaimer manquant (G2)")
    if r.ai_layer == "ai-validated" and not r.ai_synthesis:
        issues.append("ai_layer incohérent : ai-validated sans synthèse")
    if r.urgency in ("emergency", "immediate") and r.ai_synthesis:
        issues.append("cas urgent avec synthèse IA (G5)")
    return issues
