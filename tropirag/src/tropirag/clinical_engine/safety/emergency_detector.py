"""Détection d'urgences immédiates (triage de sauvetage)."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.core.enums import Urgency
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.clinical_engine.safety.red_flag_detector import RedFlagHit, detect_red_flags


@dataclass(slots=True)
class EmergencyAssessment:
    is_emergency: bool
    urgency: Urgency
    reasons: list[str]


def assess_emergency(case: ClinicalCase) -> EmergencyAssessment:
    hits = detect_red_flags(case)
    immediate = [h for h in hits if h.urgency is Urgency.IMMEDIATE]
    return EmergencyAssessment(
        is_emergency=bool(immediate),
        urgency=Urgency.IMMEDIATE if immediate else (Urgency.ROUTINE if not hits else Urgency.EMERGENCY),
        reasons=[h.message for h in immediate],
    )
