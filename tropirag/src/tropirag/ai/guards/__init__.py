"""Garde-fous IA (entrée/sortie) — aucun texte IA ne franchit ces barrières.

Ordre du pipeline :
    InputGuard (entrée)
      → [mesh IA]
    OutputGuard = AutonomousDiagnosis + Evidence + Hallucination + Clinical
"""
from __future__ import annotations

from tropirag.ai.guards.autonomous_diagnosis_guard import AutonomousDiagnosisGuard
from tropirag.ai.guards.clinical_guard import ClinicalGuard
from tropirag.ai.guards.evidence_guard import EvidenceGuard
from tropirag.ai.guards.hallucination_guard import HallucinationGuard
from tropirag.ai.guards.input_guard import (
    GuardResult,
    InputGuard,
    _fail,
    _pass,
)
from tropirag.ai.guards.output_guard import OutputGuard

__all__ = [
    "GuardResult", "InputGuard", "OutputGuard", "AutonomousDiagnosisGuard",
    "EvidenceGuard", "HallucinationGuard", "ClinicalGuard", "_fail", "_pass",
]
