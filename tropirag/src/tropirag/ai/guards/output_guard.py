"""Garde-fous IA — validation systématique des entrées ET des sorties.

Position dans le pipeline :
    INPUT GUARD   → avant toute inférence (injection, hors-périmètre)
    OUTPUT GUARDS → après toute inférence (citation, hallucination, diagnostic autonome)

Aucun texte IA ne rejoint le clinicien sans franchir ces gardes.

Architecture (chaque garde dans SON module) :
    guards/input_guard.py                → GuardResult + InputGuard (contrat commun)
    guards/autonomous_diagnosis_guard.py → AutonomousDiagnosisGuard
    guards/evidence_guard.py             → EvidenceGuard
    guards/hallucination_guard.py        → HallucinationGuard
    guards/clinical_guard.py             → ClinicalGuard
    guards/output_guard.py (ICI)         → OutputGuard (composition)

Tous les noms publics restent importables depuis ce module
(compatibilité descendante).
"""
from __future__ import annotations

from tropirag.ai.guards.autonomous_diagnosis_guard import (  # noqa: F401
    FORBIDDEN_CLAIMS,
    AutonomousDiagnosisGuard,
)
from tropirag.ai.guards.clinical_guard import (  # noqa: F401
    HEDGE_REQUIRED,
    ClinicalGuard,
)
from tropirag.ai.guards.evidence_guard import (  # noqa: F401
    EvidenceGuard,
    extract_citations,
)
from tropirag.ai.guards.hallucination_guard import HallucinationGuard  # noqa: F401
from tropirag.ai.guards.input_guard import (  # noqa: F401
    INJECTION_PATTERNS,
    OUT_OF_SCOPE_PATTERNS,
    GuardResult,
    InputGuard,
    _fail,
    _pass,
)
from tropirag.domain.evidence.entities import EvidencePack

__all__ = [
    "GuardResult", "InputGuard", "OutputGuard", "AutonomousDiagnosisGuard",
    "EvidenceGuard", "HallucinationGuard", "ClinicalGuard",
    "FORBIDDEN_CLAIMS", "HEDGE_REQUIRED", "INJECTION_PATTERNS",
    "OUT_OF_SCOPE_PATTERNS", "extract_citations", "_fail", "_pass",
]


# ---------------------------------------------------------------------------
# Output guard composé
# ---------------------------------------------------------------------------


class OutputGuard:
    """Composition des gardes de sortie — exécutées dans l'ordre du plus critique.

    Ordre immuable :
        1. AutonomousDiagnosisGuard (barrière constitutionnelle),
        2. EvidenceGuard (citations valides — fantômes rejetées),
        3. HallucinationGuard (tolérance ZÉRO : ancrage par unité citée),
        4. ClinicalGuard (finition, non bloquante).
    """

    def __init__(self) -> None:
        self.autonomous = AutonomousDiagnosisGuard()
        self.evidence = EvidenceGuard()
        # tolérance zéro : UNE affirmation clinique non ancrée → rejet
        self.hallucination = HallucinationGuard(max_unsupported=0)
        self.clinical = ClinicalGuard()

    def check(self, text: str, pack: EvidencePack, language: str = "fr") -> GuardResult:
        r1 = self.autonomous.check(text)
        if not r1.passed:
            return r1
        r2 = self.evidence.check(text, pack)
        if not r2.passed:
            return r2
        r3 = self.hallucination.check(text, pack)
        if not r3.passed:
            return r3
        r4 = self.clinical.check(text, language)
        findings = r3.findings + r4.findings
        return GuardResult(passed=True, findings=findings,
                           message=r4.message or "sortie conforme")
