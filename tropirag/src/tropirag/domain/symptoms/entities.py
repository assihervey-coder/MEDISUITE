"""Entités Symptôme — observations cliniques normalisées."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from tropirag.core.enums import SymptomCategory


@dataclass(slots=True)
class Symptom:
    """Un symptôme normalisé avec chronologie."""

    code: str                 # canonique : 'fever', 'headache'...
    label_fr: str
    category: SymptomCategory
    severity: str = "present"          # present | severe
    onset_date: date | None = None
    duration_days: float | None = None
    context: dict = field(default_factory=dict)  # ex : {"site": "jambes"} pour rash

    def within(self, other: date) -> bool:
        """Le symptôme était-il actif à `other` ? (approximation : actif depuis onset)"""
        return self.onset_date is None or self.onset_date <= other
