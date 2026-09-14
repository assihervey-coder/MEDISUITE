"""Contexte clinique partagé pour les couches IA (vue prête à injecter dans les prompts)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tropirag.clinical_engine.orchestrator import ClinicalAnalysis


@dataclass(slots=True)
class ClinicalContext:
    """Résumé structuré du cas — ce que les modèles IA ont le DROIT de voir."""

    case_summary: str
    suspected_diseases: list[str]
    red_flag_codes: list[str]
    urgency: str
    severity: str
    timeline_notes: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)  # médicaments interdits, etc.
    required_tests: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_analysis(cls, a: ClinicalAnalysis) -> "ClinicalContext":
        c = a.case
        parts = [
            f"Patient : {c.patient.age_years or '?'} ans, sexe {c.patient.sex.value}",
            f"Symptômes : {', '.join(sorted(c.symptom_codes())) or 'aucun'}",
        ]
        if c.vitals.temperature_c is not None:
            parts.append(f"Température : {c.vitals.temperature_c} °C")
        if c.timeline:
            ret = c.timeline.days_since_return()
            if ret is not None:
                parts.append(f"Retour de voyage : il y a {ret:.0f} jours ({', '.join(c.travel.countries_visited()) or '?'})")
        parts.append(f"Biologie disponible : {'oui' if c.lab_results else 'aucune'}")
        return cls(
            case_summary=" | ".join(parts),
            suspected_diseases=[d.disease for d in a.differentials if not d.excluded][:6],
            red_flag_codes=[rf.code for rf in a.rules.red_flags],
            urgency=a.safety.max_urgency.value,
            severity=a.safety.max_severity.value,
            timeline_notes=a.timeline_notes,
            constraints=[f"médicament interdit : {dc.drug} ({dc.reason})"
                         for dc in a.rules.drug_constraints if dc.forbidden],
            required_tests=list({t.test_code for t in a.rules.required_tests}),
        )
