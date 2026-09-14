"""Cas clinique — agrégat racine du domaine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from tropirag.core.enums import Severity, Urgency
from tropirag.domain.diagnostics.results import TestResult
from tropirag.domain.medications.prescriptions import MedicationOrder
from tropirag.domain.patient.entities import Patient
from tropirag.domain.patient.value_objects import VitalSigns
from tropirag.domain.symptoms.entities import Symptom
from tropirag.domain.travel.entities import TravelHistory
from tropirag.domain.travel.exposures import ExposureSummary
from tropirag.domain.travel.timeline import Timeline


@dataclass(slots=True)
class ClinicalCase:
    """Toutes les données d'un cas au moment de l'analyse."""

    case_id: str
    patient: Patient
    symptoms: list[Symptom] = field(default_factory=list)
    vitals: VitalSigns = field(default_factory=VitalSigns)
    lab_results: list[TestResult] = field(default_factory=list)
    travel: TravelHistory = field(default_factory=TravelHistory)
    exposures: ExposureSummary = field(default_factory=ExposureSummary)
    timeline: Timeline | None = None
    medications: list[MedicationOrder] = field(default_factory=list)
    free_text: str = ""
    consultation_date: date | None = None

    # --- accès rapides -----------------------------------------------------
    def symptom_codes(self) -> set[str]:
        return {s.code for s in self.symptoms}

    def has(self, code: str) -> bool:
        return code in self.symptom_codes()

    def has_any(self, codes: list[str]) -> bool:
        return any(c in self.symptom_codes() for c in codes)

    def has_all(self, codes: list[str]) -> bool:
        return all(c in self.symptom_codes() for c in codes)

    def severe_symptoms(self) -> list[Symptom]:
        return [s for s in self.symptoms if s.severity == "severe"]

    def test(self, code: str) -> TestResult | None:
        for r in self.lab_results:
            if r.test_code == code:
                return r
        return None

    def lab_value(self, code: str, component: str | None = None) -> float | None:
        for r in self.lab_results:
            if r.test_code == code and (
                component is None or component in (r.raw.get("component") or "").lower()
            ):
                if r.numeric is not None:
                    return r.numeric
        return None
