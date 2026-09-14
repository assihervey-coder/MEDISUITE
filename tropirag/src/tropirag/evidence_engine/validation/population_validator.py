"""Validation population — applicabilité selon l'âge/sexe/statut."""
from __future__ import annotations

from tropirag.domain.evidence.entities import EvidenceUnit
from tropirag.evidence_engine.validation.source_validator import ValidationResult


class PopulationValidator:
    """V1 : contrôle par mots-clés de population dans le texte de l'unité."""

    CHILD_MARKERS = ("nourrisson", "enfant", "nouveau-né", "pédiatrique")
    PREGNANCY_MARKERS = ("grossesse", "enceinte", "fœtal", "maternel")

    def validate(self, unit: EvidenceUnit, patient_profile: dict) -> ValidationResult:
        text = unit.text.lower()
        if patient_profile.get("pregnant") and any(m in text for m in self.PREGNANCY_MARKERS):
            return ValidationResult(True, "spécifiquement pertinent grossesse")
        if patient_profile.get("child") and any(m in text for m in self.CHILD_MARKERS):
            return ValidationResult(True, "spécifiquement pertinent pédiatrique")
        return ValidationResult(True)
