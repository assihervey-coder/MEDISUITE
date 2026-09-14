"""Support multilingue FR/EN des blocs de réponse."""
from __future__ import annotations

LABELS = {
    "fr": {"urgency": "Urgence", "severity": "Gravité", "differentials": "Différentiel",
           "red_flags": "Signes de gravité", "tests": "Examens recommandés",
           "constraints": "Contraintes médicamenteuses", "evidence": "Preuves",
           "citations": "Références", "disclaimer": "Avertissement"},
    "en": {"urgency": "Urgency", "severity": "Severity", "differentials": "Differentials",
           "red_flags": "Red flags", "tests": "Recommended tests",
           "constraints": "Drug constraints", "evidence": "Evidence",
           "citations": "References", "disclaimer": "Disclaimer"},
}


def labels(language: str = "fr") -> dict:
    return LABELS.get(language, LABELS["fr"])
