"""Chronologie clinique — recalage symptômes × voyage."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from tropirag.core.datetime import days_between, local_now
from tropirag.domain.travel.entities import TravelHistory


@dataclass(slots=True)
class Anchor:
    """Point d'ancrage temporel du cas."""

    consultation: date
    symptom_onset: date | None = None

    @property
    def days_since_onset(self) -> float | None:
        return days_between(self.symptom_onset, self.consultation)


@dataclass(slots=True)
class Timeline:
    """Chronologie reconstruite d'un cas."""

    anchor: Anchor
    travel: TravelHistory

    def days_since_return(self) -> float | None:
        ret = self.travel.last_return()
        return days_between(ret, self.anchor.consultation)

    def days_onset_after_return(self) -> float | None:
        """Délai entre le retour et le début des symptômes (négatif = malade avant le retour)."""
        ret = self.travel.last_return()
        return days_between(ret, self.anchor.symptom_onset) if ret and self.anchor.symptom_onset else None

    def was_traveling_at_onset(self) -> bool | None:
        if self.anchor.symptom_onset is None:
            return None
        segs = self.travel.segments_active_at(self.anchor.symptom_onset)
        return bool(segs) if segs or self.travel.segments else None

    def in_incubation_context(self, disease_window: tuple[float, float]) -> bool:
        """Le délai dernier-exposition/début est-il compatible avec la fenêtre ?

        On prend la date pivot la plus défavorable : début des symptômes vs
        dernier retour ; None → True (pas assez d'infos pour exclure).
        """
        delta = self.days_since_return() if self.anchor.symptom_onset is not None else None
        if delta is None:
            return True
        lo, hi = disease_window
        return lo <= delta <= hi


def build_timeline(consultation: date | None,
                   symptom_onset: date | None,
                   travel: TravelHistory) -> Timeline:
    return Timeline(
        anchor=Anchor(consultation=consultation or local_now().date(),
                      symptom_onset=symptom_onset),
        travel=travel,
    )
