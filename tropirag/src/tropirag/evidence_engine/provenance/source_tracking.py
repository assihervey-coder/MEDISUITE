"""Suivi des sources utilisées par requête."""
from __future__ import annotations

from collections import Counter


class SourceTracker:
    """Compte l'usage des unités par requête (audit qualité corpus)."""

    def __init__(self) -> None:
        self._usage: Counter[str] = Counter()

    def record(self, unit_ids: list[str]) -> None:
        self._usage.update(unit_ids)

    def most_used(self, n: int = 10) -> list[tuple[str, int]]:
        return self._usage.most_common(n)

    def never_used(self, all_ids: list[str]) -> list[str]:
        return [u for u in all_ids if u not in self._usage]
