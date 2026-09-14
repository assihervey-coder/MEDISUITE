"""Validation structurelle d'un cas clinique."""
from __future__ import annotations

from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.travel.validators import validate_segment


def validate_case(case: ClinicalCase) -> list[str]:
    issues: list[str] = []
    if not case.symptoms:
        issues.append("Aucun symptôme documenté — analyse impossible sans données cliniques")
    if case.patient.age_years is None:
        issues.append("Âge patient manquant — recommandé pour pondérer le différentiel")
    for seg in case.travel.segments:
        issues.extend(validate_segment(seg))
    if case.vitals.temperature_c is not None and case.vitals.temperature_c > 45:
        issues.append("Température improbable — vérifier la saisie")
    for s in case.symptoms:
        if s.onset_date and case.consultation_date and s.onset_date > case.consultation_date:
            issues.append(f"Symptôme {s.code}: début postérieur à la consultation")
    return issues
