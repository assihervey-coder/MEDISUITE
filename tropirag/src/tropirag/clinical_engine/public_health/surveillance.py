"""Surveillance de santé publique (comptage des cas, signaux)."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass(slots=True)
class SurveillanceSignal:
    disease: str
    case_count: int
    note: str


class SurveillanceTracker:
    """Registre mémoire des suspicions par maladie (agrégation locale)."""

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._notifiable: list[dict] = []

    def record_case(self, diseases: list[str]) -> None:
        self._counts.update(diseases)

    def record_notification(self, notif: dict) -> None:
        self._notifiable.append(notif)

    def signals(self) -> list[SurveillanceSignal]:
        return [SurveillanceSignal(d, n, f"{n} cas suspects cumulés") for d, n in self._counts.most_common()]

    def snapshot(self) -> dict:
        return {"counts": dict(self._counts), "notifiable": self._notifiable}
