"""Validation de juridiction — la recommandation s'applique-t-elle ici ?"""
from __future__ import annotations

from tropirag.domain.evidence.entities import EvidenceUnit
from tropirag.evidence_engine.validation.source_validator import ValidationResult


class JurisdictionValidator:

    def validate(self, unit: EvidenceUnit, jurisdiction: str) -> ValidationResult:
        if unit.jurisdiction == "INT":
            return ValidationResult(True)
        if unit.jurisdiction == jurisdiction:
            return ValidationResult(True)
        return ValidationResult(False, f"unité {unit.jurisdiction} non applicable en {jurisdiction}")
