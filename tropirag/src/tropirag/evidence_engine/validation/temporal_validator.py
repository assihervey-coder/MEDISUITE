"""Validation temporelle — une preuve périmée ne sort pas dans le pack actif."""
from __future__ import annotations

from datetime import date

from tropirag.domain.evidence.entities import EvidenceUnit
from tropirag.evidence_engine.validation.source_validator import ValidationResult


class TemporalValidator:
    """valid_until dépassé ou superseded_by → exclu (mais gardé en base)."""

    def validate(self, unit: EvidenceUnit, ref: date | None = None) -> ValidationResult:
        if not unit.is_current(ref):
            return ValidationResult(False, "unité périmée ou remplacée")
        return ValidationResult(True)
