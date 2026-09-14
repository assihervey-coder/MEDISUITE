"""Relations entre maladies (sévérité, hiérarchies)."""
from __future__ import annotations

# Maladie bénigne → forme sévère correspondante
SEVERE_FORM: dict[str, str] = {
    "malaria": "severe_malaria",
    "dengue": "severe_dengue",
}

# Groupes nosologiques pour la présentation du différentiel
DISEASE_GROUPS: dict[str, list[str]] = {
    "parasitic": ["malaria", "severe_malaria"],
    "arboviruses": ["dengue", "severe_dengue", "chikungunya", "zika", "yellow_fever"],
    "bacterial": ["enteric_fever", "meningococcal", "leptospirosis", "rickettsial"],
    "viral_hemorrhagic": ["ebola", "marburg", "lassa"],
    "viral_other": ["influenza", "covid19", "hepatitis_a"],
}
