"""Moteur de chronologie — reconstruction, cohérence, récit temporel.

Reconstruit la ligne de temps d'un cas (segments de voyage → incubation →
symptômes → consultation) et détecte les incohérences temporelles :
symptômes antérieurs au retour, dates impossibles, incubations incompatibles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from tropirag.clinical_engine.temporal.incubation_engine import TemporalReasoner
from tropirag.domain.clinical_case.entities import ClinicalCase


@dataclass(slots=True)
class TimelineEvent:
    date: str
    label: str
    kind: str             # exposure | symptom | test | consultation


@dataclass(slots=True)
class TimelineReport:
    events: list[TimelineEvent] = field(default_factory=list)
    incoherences: list[str] = field(default_factory=list)

    @property
    def coherent(self) -> bool:
        return not self.incoherences


class TimelineEngine:
    """Reconstruction chronologique + contrôles de cohérence."""

    def __init__(self) -> None:
        self._reasoner = TemporalReasoner()

    # ------------------------------------------------------------------
    def build(self, case: ClinicalCase) -> TimelineReport:
        report = TimelineReport()
        travel = case.travel

        # segments de voyage (arrivée/départ par pays)
        for seg in travel.segments:
            if seg.arrival:
                report.events.append(TimelineEvent(
                    seg.arrival.isoformat(),
                    f"Arrivée {seg.country}" + (f" ({seg.region})" if seg.region else ""),
                    "exposure"))
            if seg.departure:
                report.events.append(TimelineEvent(
                    seg.departure.isoformat(), f"Retour de {seg.country}",
                    "exposure"))
            if seg.arrival and seg.departure and seg.departure < seg.arrival:
                report.incoherences.append(
                    f"segment {seg.country}: départ antérieur à l'arrivée — "
                    "dates saisies incohérentes")

        last_return = travel.last_return()

        # symptômes avec date d'apparition
        for s in case.symptoms:
            if s.onset_date:
                report.events.append(TimelineEvent(
                    s.onset_date.isoformat(), f"Début : {s.code}", "symptom"))
                if last_return and s.onset_date < last_return:
                    report.incoherences.append(
                        f"symptôme {s.code} déclaré AVANT le retour de voyage "
                        f"({s.onset_date} < {last_return}) — vérifier la saisie "
                        "ou élargir l'anamnèse")

        # biologie réalisée (jour de prélèvement implicite = consultation)
        for lr in case.lab_results:
            report.events.append(TimelineEvent(
                (case.consultation_date or date.today()).isoformat(),
                f"Examen : {lr.test_code if hasattr(lr, 'test_code') else 'lab'}",
                "test"))

        # consultation = ancrage
        report.events.append(TimelineEvent(
            (case.consultation_date or date.today()).isoformat(),
            "Consultation", "consultation"))

        report.events.sort(key=lambda e: e.date)
        return report

    # ------------------------------------------------------------------
    def narrate(self, case: ClinicalCase) -> list[str]:
        """Récit temporel lisible (compatibilité avec l'orchestrateur)."""
        return self._reasoner.narrate(case)

    def narrative(self, case: ClinicalCase) -> list[str]:
        """Récit enrichi : ligne de temps + incohérences explicites."""
        report = self.build(case)
        lines = [f"{e.date} — {e.label}" for e in report.events]
        if report.incoherences:
            lines.append("⚠ Incohérences temporelles : " + " ; ".join(report.incoherences))
        lines.extend(self._reasoner.narrate(case))
        return lines


def narrate_timeline(case: ClinicalCase) -> list[str]:
    """Compatibilité — délègue au moteur de chronologie enrichi."""
    return TimelineEngine().narrative(case)
