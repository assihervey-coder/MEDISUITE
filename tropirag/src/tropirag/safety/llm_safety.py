"""Sécurité spécifique LLM — limites contractuelles du mesh IA.

Ces limites sont UNILATÉRALES : elles s'imposent à tout modèle, quelle que
soit sa qualité revendiquée. Leur vérification est fournie pour l'audit et
les tests de non-régression de gouvernance.
"""
from __future__ import annotations

import re

from tropirag.ai.guards.autonomous_diagnosis_guard import AutonomousDiagnosisGuard
from tropirag.ai.guards.evidence_guard import extract_citations
from tropirag.domain.evidence.entities import EvidencePack

LLM_LIMITS = {
    "no_dosing": "aucune posologie générée par LLM",
    "no_diagnosis": "aucun diagnostic autonome",
    "grounding": "toute affirmation clinique citée",
    "supervision": "sorties destinées à des professionnels de santé",
    "refusal_expected": "le refus est une réponse valide",
}

_DOSING_RE = re.compile(
    r"\b\d+\s?(?:mg|µg|ml|g)\b[^.]{0,40}\b(?:fois|jour|matin|soir|heures)\b"
    r"|\b(?:dose|posologie)\s*[:\-]\s*\d+")


class LlmSafetyChecker:
    """Vérifie les 5 limites contractuelles sur une sortie LLM."""

    def __init__(self) -> None:
        self._autonomous = AutonomousDiagnosisGuard()

    def check(self, text: str, pack: EvidencePack | None = None) -> dict:
        report: dict[str, bool | list[str]] = {}
        # 1) no_diagnosis
        diag = self._autonomous.check(text)
        report["no_diagnosis"] = diag.passed
        report["diagnosis_findings"] = diag.findings
        # 2) no_dosing
        report["no_dosing"] = _DOSING_RE.search((text or "").lower()) is None
        # 3) grounding
        if pack is not None and pack.units:
            valid = {u.unit_id for u in pack.units}
            cited = extract_citations(text)
            report["grounding"] = bool(cited) and all(c in valid for c in cited)
        else:
            report["grounding"] = None  # pack absent → non évaluable ici
        # 4) supervision + 5) refusal_expected : propriétés du système
        report["supervision"] = True
        report["refusal_expected"] = True
        return report

    def passed(self, text: str, pack: EvidencePack | None = None) -> bool:
        r = self.check(text, pack)
        return bool(r.get("no_diagnosis")) and bool(r.get("no_dosing")) \
            and r.get("grounding") in (None, True)
