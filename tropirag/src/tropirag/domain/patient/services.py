"""Services Patient (helpers métier purs)."""
from __future__ import annotations

from tropirag.domain.patient.entities import Patient


def dosing_weight(patient: Patient, default: float = 60.0) -> float:
    """Poids pour calcul de dose ; défaut adulte SI (jamais utilisé pour prescrire)."""
    return patient.weight_kg or (10.0 if patient.is_child() else default)


def pediatric_red_flag_age(patient: Patient) -> bool:
    """Nourrisson < 12 mois avec fièvre = vulnérabilité accrue."""
    return patient.is_infant()
