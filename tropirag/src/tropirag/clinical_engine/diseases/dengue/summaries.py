"""Spécialisation dengue — signes d'alarme OMS."""
from __future__ import annotations

WARNING_SIGNS_WHO = [
    ("abdominal_pain", "Douleur abdominale intense"),
    ("persistent_vomiting", "Vomissements persistants"),
    ("fluid_accumulation", "Épanchement (ascite, pleural)"),
    ("mucosal_bleeding", "Saignements muqueux"),
    ("lethargy", "Léthargie / agitation"),
    ("hepatomegaly", "Hépatomégalie douloureuse"),
    ("rising_hct", "Hématocrite croissant + plaquettes chutant"),
]

SEVERE_CRITERIA = [
    ("shock", "Choc / collapsus"),
    ("respiratory_distress", "Détresse respiratoire par extravasation"),
    ("severe_bleeding", "Hémorragie sévère"),
    ("organ_impairment", "Défaillance d'organe (foie, rein, encéphale)"),
]
