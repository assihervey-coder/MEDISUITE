"""Contraintes médicamenteuses par contexte clinique (déterministe)."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.domain.medications.entities import DRUGS

# V1.1 — drapeaux grossesse/précarité rénaux qui impliquent une CI générique AINS
_AVOID_NSAIDS_FLAGS = ("third_trimester", "dehydration_scd")


@dataclass(slots=True)
class DrugConstraintResult:
    drug_code: str
    allowed: bool
    reason: str | None = None
    severity: str = "info"          # info | warning | danger


def check_drug_for_context(drug_code: str, suspected: list[str],
                           patient_flags: list[str]) -> DrugConstraintResult:
    """Vérifie un médicament contre les suspicions actives + drapeaux patient.

    patient_flags : 'pregnancy', 'child', 'renal_failure', 'hepatic_failure',
                    'cardiac_arrhythmia', 'gastric_ulcer', 'jaundice_neonate',
                    'first_trimester', 'third_trimester', 'sickle_cell',
                    'g6pd_deficient', 'dehydration_scd'...
    """
    drug = DRUGS.get(drug_code)
    if drug is None:
        return DrugConstraintResult(drug_code, allowed=True,
                                    reason="Médicament hors référentiel — vérification manuelle requise",
                                    severity="warning")
    for disease in suspected:
        if disease in drug.contraindicated_in:
            return DrugConstraintResult(drug_code, allowed=False,
                                        reason=drug.contraindicated_in[disease], severity="danger")
    for flag in patient_flags:
        key = flag
        if key in drug.contraindicated_in:
            return DrugConstraintResult(drug_code, allowed=False,
                                        reason=drug.contraindicated_in[key], severity="danger")
        if flag == "pregnancy" and drug.pregnancy_category in ("D", "X"):
            return DrugConstraintResult(drug_code, allowed=False,
                                        reason=f"Catégorie grossesse {drug.pregnancy_category}", severity="danger")
        if flag == "child" and key == "child_viral":
            continue
    # V1.1 — grossesse : AINS réservés au 1er/2e trimestre à dose minimale (OMS)
    if "pregnancy" in patient_flags and drug.drug_class == "AINS":
        if not any(f in patient_flags for f in ("first_trimester", "second_trimester", "third_trimester")):
            return DrugConstraintResult(
                drug_code, allowed=True,
                reason="AINS pendant la grossesse : paracétamol à privilégier ; si AINS indispensable, "
                       "dose minimale la plus courte possible",
                severity="warning")
    for f in _AVOID_NSAIDS_FLAGS:
        if f in patient_flags and drug.drug_class == "AINS":
            return DrugConstraintResult(drug_code, allowed=False,
                                        reason=drug.contraindicated_in.get(
                                            f, "AINS contre-indiqué dans ce contexte"),
                                        severity="danger")
    return DrugConstraintResult(drug_code, allowed=True)
