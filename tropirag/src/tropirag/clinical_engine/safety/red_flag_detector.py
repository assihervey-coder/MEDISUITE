"""Détection de red flags indépendante du référentiel YAML (double filet).

Objectif : si le Rule Engine échoue, ce détecteur minimal capture les
urgences vitales de base. Défense en profondeur — jamais une seule couche.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.core.enums import Severity, Urgency
from tropirag.domain.clinical_case.entities import ClinicalCase

_CRITICAL_SYMPTOMS = {
    "coma": "Trouble de conscience",
    "convulsions": "Convulsions",
    "hematemesis": "Hématémèse",
    "melena": "Méléna",
    "prostration": "Prostration",
    "abnormal_bleeding": "Saignements anormaux",
    "neck_stiffness": "Raideur de nuque",
    "petechiae": "Purpura",
}


@dataclass(slots=True)
class RedFlagHit:
    code: str
    severity: Severity
    urgency: Urgency
    message: str


def detect_red_flags(case: ClinicalCase) -> list[RedFlagHit]:
    hits: list[RedFlagHit] = []
    codes = case.symptom_codes()
    for code, label in _CRITICAL_SYMPTOMS.items():
        if code in codes:
            hits.append(RedFlagHit(code, Severity.CRITICAL, Urgency.IMMEDIATE,
                                   f"{label} — urgence vitale (détection directe)"))
    if case.vitals.is_hypotension():
        hits.append(RedFlagHit("hypotension", Severity.CRITICAL, Urgency.IMMEDIATE,
                                "Hypotension < 90 mmHg (détection directe)"))
    if case.vitals.is_hypoxia():
        hits.append(RedFlagHit("hypoxia", Severity.CRITICAL, Urgency.IMMEDIATE,
                                "Hypoxie SpO2 < 92 % (détection directe)"))
    return hits
