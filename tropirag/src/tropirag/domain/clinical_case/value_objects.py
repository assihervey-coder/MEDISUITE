"""Objets-valeurs du cas clinique."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.core.enums import Severity, Urgency


@dataclass(slots=True)
class CaseVerdict:
    """Verdict déterministe global du cas."""

    urgency: Urgency = Urgency.ROUTINE
    severity: Severity = Severity.NONE
    requires_isolation: bool = False
    must_not_miss_active: bool = False
    refuse_synthesis: bool = False
    refusal_reason: str | None = None
