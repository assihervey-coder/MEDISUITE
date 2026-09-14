"""Contexte de décision — contrat structuré entre le noyau déterministe et l'IA.

Le DecisionContext est le SEUL objet qu'un modèle reçoit comme contexte
clinique. Il est construit de façon déterministe depuis l'analyse, et
chaque champ est audité : le modèle ne voit jamais de données brutes non
structurées.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tropirag.clinical_engine.clinical_context import ClinicalContext  # noqa: F401

if TYPE_CHECKING:  # pragma: no cover
    from tropirag.clinical_engine.orchestrator import ClinicalAnalysis


@dataclass(slots=True)
class DecisionContext:
    """Vue synthétique d'un cas — entrée contractuelle des modèles IA."""

    case_id: str = ""
    urgency: str = "routine"
    severity: str = "none"
    patient_summary: str = ""
    symptom_codes: list[str] = field(default_factory=list)
    travel_summary: str = ""
    differential_summary: list[dict] = field(default_factory=list)
    matched_rules: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    ai_allowed: bool = True
    ai_block_reason: str = ""

    def render(self) -> str:
        """Rendu texte compact injectable dans un prompt (contrôlé)."""
        parts = [
            f"CAS {self.case_id} — urgence: {self.urgency}, sévérité: {self.severity}",
            f"Patient: {self.patient_summary}" if self.patient_summary else "",
            f"Symptômes: {', '.join(self.symptom_codes)}"
            if self.symptom_codes else "",
            f"Voyage: {self.travel_summary}" if self.travel_summary else "",
            "Différentiel: " + "; ".join(
                f"{d.get('disease')} (p={d.get('probability')})"
                for d in self.differential_summary) if self.differential_summary else "",
            f"Règles matchées: {', '.join(self.matched_rules)}"
            if self.matched_rules else "",
            f"Drapeaux rouges: {', '.join(self.red_flags)}" if self.red_flags else "",
            "Contraintes: " + "; ".join(self.constraints) if self.constraints else "",
            "Interdits: " + "; ".join(self.forbidden) if self.forbidden else "",
        ]
        return "\n".join(p for p in parts if p)


def build_decision_context(analysis: "ClinicalAnalysis") -> DecisionContext:
    """Analyse déterministe → contexte de décision IA (100 % audité)."""
    case = analysis.case
    patient = case.patient
    safety = analysis.safety
    escalation = analysis.escalation

    # blocage IA : verdict du safety engine (cas critiques → déterministe pur)
    verdict = getattr(safety, "verdict", None)
    ai_allowed = not getattr(verdict, "ai_synthesis_blocked", False) \
        if verdict is not None else True
    ai_block_reason = ""
    if not ai_allowed:
        ai_block_reason = "; ".join(safety.blocking_messages) or \
            "cas critique — réponse déterministe pure"

    # résumé voyage : segments pays/dates
    countries = case.travel.countries_visited()
    travel_bits = []
    if countries:
        travel_bits.append("pays: " + ", ".join(countries))
    last_return = case.travel.last_return()
    if last_return:
        travel_bits.append(f"retour le {last_return.isoformat()}")

    return DecisionContext(
        case_id=case.case_id,
        urgency=safety.max_urgency.value,
        severity=safety.max_severity.value,
        patient_summary=(
            f"{patient.age_years} ans, {patient.sex.value}"
            + (", enceinte" if getattr(patient.pregnant, "value", "") == "pregnant" else "")
            + (f" ({', '.join(patient.chronic_conditions)})"
               if patient.chronic_conditions else "")),
        symptom_codes=[s.code for s in case.symptoms],
        travel_summary=" ; ".join(travel_bits),
        differential_summary=[
            {"disease": str(d.disease),
             "probability": round(float(getattr(d, "score", 0.0)), 3),
             "rank": i + 1}
            for i, d in enumerate(analysis.differentials[:6])],
        matched_rules=analysis.matched_rule_ids,
        red_flags=list(safety.red_flag_codes),
        constraints=list(escalation.messages),
        forbidden=[],
        ai_allowed=ai_allowed,
        ai_block_reason=ai_block_reason,
    )
