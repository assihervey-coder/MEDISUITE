"""Objets-valeurs Patient (poids, âge gestationnel, scores simples)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Anthropometry:
    weight_kg: float | None = None
    height_cm: float | None = None

    def bmi(self) -> float | None:
        if self.weight_kg and self.height_cm:
            return round(self.weight_kg / (self.height_cm / 100) ** 2, 1)
        return None

    def weight_for_dosing(self) -> float | None:
        return self.weight_kg


@dataclass(slots=True)
class VitalSigns:
    """Constantes — None = non mesuré (jamais inventé)."""

    temperature_c: float | None = None
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    heart_rate: int | None = None
    respiratory_rate: int | None = None
    spo2_pct: float | None = None
    capillary_refill_s: float | None = None
    consciousness: str | None = None  # AVPU: alert/voice/pain/unresponsive

    def is_fever(self, threshold: float = 38.0) -> bool:
        return self.temperature_c is not None and self.temperature_c >= threshold

    def is_hypotension(self, threshold: int = 90) -> bool:
        return self.systolic_bp is not None and self.systolic_bp < threshold

    def is_tachypnea_adult(self, threshold: int = 24) -> bool:
        return self.respiratory_rate is not None and self.respiratory_rate >= threshold

    def is_hypoxia(self, threshold: float = 92.0) -> bool:
        return self.spo2_pct is not None and self.spo2_pct < threshold

    def is_unresponsive(self) -> bool:
        return self.consciousness in ("unresponsive", "U", "coma", "P")


@dataclass(slots=True)
class FluidStatus:
    """Statut volémique simple (choc ?)."""

    dehydrated: bool = False
    unable_to_drink: bool = False
    urine_output_low: bool = False
