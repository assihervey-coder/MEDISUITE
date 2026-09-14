"""Spécialisation paludisme — résumés cliniques structurés."""
from __future__ import annotations

SEVERE_CRITERIA_WHO = [
    ("coma_confusion", "Trouble de conscience"),
    ("prostration", "Prostration"),
    ("convulsions", "Convulsions multiples"),
    ("acidosis", "Acidose métabolique"),
    ("hypoglycemia", "Hypoglycémie"),
    ("severe_anemia", "Anémie sévère Hb < 7 g/dL"),
    ("renal", "Insuffisance rénale / oligurie"),
    ("jaundice_parasitemia", "Ictère + parasitémie élevée"),
    ("pulmonary_edema", "Œdème pulmonaire / détresse"),
    ("hyperparasitemia", "Hyperparasitémie ≥ 10 % (non immune)"),
]


def severe_criteria_summary(found: list[str]) -> dict:
    return {
        "criteria_found": [c for k, c in SEVERE_CRITERIA_WHO if k in found],
        "count": len([k for k, _ in SEVERE_CRITERIA_WHO if k in found]),
        "threshold": 1,
        "statement": "Un seul critère OMS suffit à définir le paludisme sévère → artésunate IV.",
    }
