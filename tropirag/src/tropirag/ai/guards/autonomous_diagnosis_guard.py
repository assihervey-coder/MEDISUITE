"""Garde anti-diagnostic-autonome — la barrière constitutionnelle de TropiRAG.

Aucune sortie IA ne peut affirmer un diagnostic, une certitude ou une
posologie. La détection est purement lexicale et déterministe — elle ne
dépend d'AUCUN modèle, elle ne peut donc pas être contournée par un modèle.
"""
from __future__ import annotations

import re

from tropirag.ai.guards.input_guard import GuardResult, _fail, _pass
from tropirag.core.enums import RefusalReason

# (motif, libellé du motif de rejet)
FORBIDDEN_CLAIMS: list[tuple[str, str]] = [
    (r"\bdiagnostic (?:certain|confirmé|d[ée]finitif)\b", "claim de diagnostic certain"),
    (r"\bc'est certainement\s+\w+", "affirmation excessive"),
    (r"\bje (?:confirme|garantis)\b", "surconfiance"),
    (r"\b(?:dose exacte|posologie pr[ée]cise)\s*:", "posologie par LLM"),
    (r"\b(?:dose|posologie)\s*[:\-]\s*\d+", "posologie par LLM"),
    (r"\b\d+\s?(?:mg|µg|ml)\b[^.]{0,40}\b(?:fois|jour|matin|soir|heures)\b",
     "posologie détaillée par LLM"),
    (r"\b100\s*%\s*(?:de chances|s[ûu]r)\b", "certitude chiffrée injustifiée"),
    (r"\b(?:efficace|efficacit[é]|gu[é]rit|remont[é]e)\s+[àa]\s*100\s*%",
     "certitude chiffrée injustifiée"),
    (r"\b\d+\s*%\s+(?:de\s+)?(?:gu[é]rison|efficacit[é])\b", "promesse de guérison chiffrée"),
    (r"\bje (?:prescris|administre)\b", "acte prescriptif par LLM"),
    (r"\ble traitement (?:est|doit être) .*imm[ée]diat sans avis", "CCT sans professionnel"),
]


class AutonomousDiagnosisGuard:
    """Refuse toute sortie qui affirme un diagnostic autonome."""

    def check(self, text: str) -> GuardResult:
        low = (text or "").lower()
        for pat, label in FORBIDDEN_CLAIMS:
            if re.search(pat, low):
                return _fail(
                    RefusalReason.AUTONOMOUS_DIAGNOSIS_FORBIDDEN,
                    f"Sortie rejetée : {label}. TropiRAG n'émet jamais de diagnostic.",
                    [label])
        return _pass()

    def findings(self, text: str) -> list[str]:
        """Mode inspection : liste les motifs sans bloquer (audit/métriques)."""
        low = (text or "").lower()
        return [label for pat, label in FORBIDDEN_CLAIMS if re.search(pat, low)]
