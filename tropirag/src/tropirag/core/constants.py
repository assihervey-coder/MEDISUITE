"""Constantes cliniques et techniques partagées."""
from __future__ import annotations

APP_NAME = "TropiRAG"
APP_TAGLINE = "Compagnon clinique de terrain — fièvre + voyage"

# Fenêtres d'incubation (jours) — sources : CDC/OMS (voir rules YAML pour citations)
INCUBATION_WINDOWS_DAYS: dict[str, tuple[float, float]] = {
    "malaria_falciparum": (7, 90),
    "dengue": (3, 14),
    "chikungunya": (2, 12),
    "zika": (3, 14),
    "yellow_fever": (3, 6),
    "enteric_fever": (6, 30),
    "ebola": (2, 21),
    "marburg": (2, 21),
    "lassa": (6, 21),
    "meningococcal": (2, 10),
    "rickettsial": (2, 14),
    "leptospirosis": (5, 14),
    "influenza": (1, 4),
    "covid19": (2, 14),
    "hepatitis_a": (14, 50),
}

# Températures seuils (°C)
FEVER_THRESHOLD_C = 38.0
HIGH_FEVER_C = 39.5
HYPOTENSION_SYSTOLIC = 90

# Hémogramme : seuils d'alerte
SEVERE_ANEMIA_HB = 7.0        # g/dL — critère paludisme sévère OMS
MODERATE_ANEMIA_HB = 9.0
THROMBOCYTOPENIA_PLT = 100_000  # /µL — signal dengue / paludisme
SEVERE_THROMBOCYTOPENIA_PLT = 50_000
LEUKOPENIA_WBC = 4_000
CREATININE_ELEVATED_UMOL = 110

# Disclaimer clinique obligatoire (toute réponse)
CLINICAL_DISCLAIMER_FR = (
    "TropiRAG est une aide à la décision destinée aux professionnels de santé. "
    "Il ne pose pas de diagnostic et ne remplace pas l'évaluation clinique. "
    "Toute décision thérapeutique relève du clinicien."
)
CLINICAL_DISCLAIMER_EN = (
    "TropiRAG is a clinical decision-support tool for healthcare professionals. "
    "It does not provide a diagnosis and does not replace clinical judgement. "
    "All therapeutic decisions rest with the clinician."
)
