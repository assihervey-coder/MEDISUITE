"""Risk Router — contraintes de sécurité clinique sur le routage."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.core.enums import Severity, Urgency

# Plus le cas est grave, plus le niveau de supervision exigé est haut
_RISK_FLOOR = {
    Severity.NONE: "none",
    Severity.MILD: "none",
    Severity.MODERATE: "assisted",
    Severity.SEVERE: "supervised",
    Severity.CRITICAL: "supervised",
}


@dataclass(slots=True)
class RiskRouting:
    clinical_risk_max: str
    ai_synthesis_allowed: bool
    reason: str


def route_by_risk(severity: Severity, urgency: Urgency) -> RiskRouting:
    """En cas critique : la synthèse IA est suspendue — les règles parlent seules."""
    floor = _RISK_FLOOR.get(severity, "supervised")
    if severity in (Severity.SEVERE, Severity.CRITICAL) or urgency in (Urgency.EMERGENCY, Urgency.IMMEDIATE):
        return RiskRouting("supervised", False,
                           "Cas grave/urgent : réponse déterministe uniquement (règles + preuves), synthèse IA suspendue")
    if severity is Severity.MODERATE:
        return RiskRouting("assisted", True,
                           "Cas modéré : synthèse IA autorisée sous supervision avec preuves")
    return RiskRouting("none", True, "Cas simple : synthèse IA encadrée autorisée")
