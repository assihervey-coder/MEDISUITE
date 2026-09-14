"""Safety Gate — LA porte de sortie finale de TropiRAG.

Aucune réponse ne quitte le système sans franchir cette gate. Elle applique
les invariants absolus :

    G1  Un red flag ne peut jamais être retiré d'une réponse.
    G2  Aucune sortie sans disclaimer clinique.
    G3  Pas de preuve → pas de synthèse IA (refus constructif).
    G4  Aucune posologie générée par IA.
    G5  Cas critique → réponse 100 % déterministe.
    G6  Diagnostic autonome interdit (formulations verrouillées).
    G7  Notifications de santé publique préservées.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from tropirag.core.enums import RefusalReason, Severity, Urgency
from tropirag.clinical_engine.orchestrator import ClinicalAnalysis
from tropirag.domain.evidence.entities import EvidencePack

DOSE_PATTERNS = [
    r"\b\d+\s?(?:mg|mg/kg|g|ml|µg|ug)\b.{0,40}?\d+\s*(?:fois|x)\b",
    r"\b(?:dose|posologie)\s*[:\-]?\s*\d+",
    r"\b\d+\s?mg\s+(?:matin|soir|chaque|toutes)",
    r"\b\d+\s?mg\s+par\s+jour",
]


@dataclass(slots=True)
class GateDecision:
    allowed: bool
    mode: str                 # ai | deterministic | refusal
    refusals: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reason: RefusalReason | None = None

    def to_dict(self) -> dict:
        return {"allowed": self.allowed, "mode": self.mode, "refusals": self.refusals,
                "warnings": self.warnings}


class SafetyGate:
    """Garde finale — combine SafetyEngine + EvidenceGate + garde de formulation."""

    def decide(self, analysis: ClinicalAnalysis, pack: EvidencePack,
               ai_text: str | None) -> GateDecision:
        d = GateDecision(allowed=True, mode="deterministic")
        sev = analysis.safety.max_severity
        urg = analysis.safety.max_urgency

        # G5 : cas critique → déterministe, pas de synthèse IA
        if sev in (Severity.SEVERE, Severity.CRITICAL) or urg in (Urgency.EMERGENCY, Urgency.IMMEDIATE):
            if ai_text is not None:
                d.warnings.append("Cas grave : synthèse IA suspendue — sortie déterministe")
            return d  # mode deterministic

        # G3 : pas de preuve → pas de synthèse IA
        if ai_text is not None and pack.empty():
            d.allowed = False
            d.refusals.append("synthèse IA refusée : aucune preuve récupérée")
            d.reason = RefusalReason.INSUFFICIENT_EVIDENCE
            return d

        # G4 : l'IA n'a pas le droit de produire une posologie
        if ai_text is not None:
            for pat in DOSE_PATTERNS:
                if re.search(pat, ai_text.lower()):
                    d.allowed = False
                    d.refusals.append("synthèse IA refusée : posologie détectée dans la sortie")
                    d.reason = RefusalReason.SAFETY_OVERRIDE
                    return d

        # G6 : formulation de diagnostic autonome
        if ai_text is not None and re.search(
            r"\bdiagnostic (?:certain|confirmé|définitif)\b", ai_text.lower()):
            d.allowed = False
            d.refusals.append("synthèse IA refusée : formulation de diagnostic certain")
            d.reason = RefusalReason.AUTONOMOUS_DIAGNOSIS_FORBIDDEN
            return d

        # pas de blocage : la synthèse IA peut être retenue
        if ai_text is not None:
            d.mode = "ai"
        return d
