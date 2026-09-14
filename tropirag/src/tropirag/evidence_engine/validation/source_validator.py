"""Validation de source — autorité connue + métadonnées complètes."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.core.enums import SourceAuthority
from tropirag.domain.evidence.entities import EvidenceUnit


@dataclass(slots=True)
class ValidationResult:
    passed: bool
    reason: str = ""


class SourceValidator:
    """Une preuve n'entre dans l'index que si sa source est authentifiée."""

    KNOWN = {a.value for a in SourceAuthority}

    def validate(self, unit: EvidenceUnit) -> ValidationResult:
        if unit.source.authority.value not in self.KNOWN:
            return ValidationResult(False, f"autorité inconnue: {unit.source.authority}")
        if not unit.source.title or not unit.source.publisher:
            return ValidationResult(False, "source sans titre ni éditeur")
        if unit.source.authority is SourceAuthority.UNKNOWN and not unit.source.url:
            return ValidationResult(False, "source inconnue sans référence")
        return ValidationResult(True)
