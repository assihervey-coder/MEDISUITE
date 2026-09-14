"""Constructeur de réponse clinique — 100 % déterministe, citée, structurée.

C'est la voix officielle de TropiRAG. Toute section affichée ici vient :
    - des règles (différentiel, red flags, escalade, tests, contraintes),
    - des preuves (citations),
    - du moteur temporel (chronologie).
Aucun texte IA ne franchit cette couche sans avoir passé la Safety Gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.clinical_engine.orchestrator import ClinicalAnalysis
from tropirag.core.constants import CLINICAL_DISCLAIMER_FR
from tropirag.domain.diseases.entities import DISEASES
from tropirag.domain.evidence.entities import EvidencePack
from tropirag.safety.clinical_safety import disclaimer
from tropirag.safety.clinical_safety import disclaimer as _disclaimer


@dataclass(slots=True)
class ClinicalResponse:
    """Réponse finale complète, prête pour l'API."""

    case_id: str
    urgency: str
    severity: str
    narrative: str = ""
    differentials: list[dict] = field(default_factory=list)
    red_flags: list[dict] = field(default_factory=list)
    escalations: list[dict] = field(default_factory=list)
    required_tests: list[dict] = field(default_factory=list)
    drug_constraints: list[dict] = field(default_factory=list)
    timeline_notes: list[str] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    notifications: list[dict] = field(default_factory=list)
    uncertainty: dict = field(default_factory=dict)
    uncertainty_notes: list[str] = field(default_factory=list)
    ai_layer: str = "deterministic"      # deterministic | ai-validated
    ai_synthesis: str | None = None
    audit_summary: dict = field(default_factory=dict)
    refusal: str | None = None
    disclaimer: str = ""
    provenance: dict = field(default_factory=dict)
    matched_rule_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "urgency": self.urgency,
            "severity": self.severity,
            "narrative": self.narrative,
            "differentials": self.differentials,
            "red_flags": self.red_flags,
            "escalations": self.escalations,
            "required_tests": self.required_tests,
            "drug_constraints": self.drug_constraints,
            "timeline_notes": self.timeline_notes,
            "citations": self.citations,
            "notifications": self.notifications,
            "uncertainty": self.uncertainty,
            "uncertainty_notes": self.uncertainty_notes,
            "ai_layer": self.ai_layer,
            "ai_synthesis": self.ai_synthesis,
            "audit_summary": self.audit_summary,
            "refusal": self.refusal,
            "disclaimer": self.disclaimer,
            "matched_rule_ids": self.matched_rule_ids,
        }


# ---------------------------------------------------------------------------
# Narrative déterministe
# ---------------------------------------------------------------------------

_URGENCY_FR = {
    "immediate": "URGENCE VITALE IMMÉDIATE",
    "emergency": "URGENCE",
    "priority": "PRIORITAIRE",
    "routine": "Consultation de routine",
}
_SEV_FR = {
    "critical": "critique", "severe": "sévère", "moderate": "modérée",
    "mild": "légère", "none": "absente",
}


def build_narrative(analysis: ClinicalAnalysis, pack: EvidencePack) -> str:
    """Synthèse narrative déterministe — chaque phrase est traçable à une règle."""
    c = analysis.case
    sev = _SEV_FR.get(analysis.safety.max_severity.value, "inconnue")
    urg = _URGENCY_FR.get(analysis.safety.max_urgency.value, "inconnue")
    lines: list[str] = []

    # 1. — En-tête clinique
    age = c.patient.age_years
    subj = f"Patient{'e' if c.patient.sex == 'female' else ''} de {age} ans" if age else "Patient"
    lines.append(f"{subj}. Gravité estimée : {sev}. Niveau de prise en charge : {urg}.")

    # 2. — Chronologie
    lines.extend(analysis.timeline_notes)

    # 3. — Red flags d'abord (toujours en tête)
    if analysis.rules.red_flags:
        lines.append("SIGNES DE GRAVITÉ :")
        for rf in analysis.rules.red_flags:
            lines.append(f"• {rf.message}")
    else:
        lines.append("Aucun signe de gravité immédiat détecté par les règles.")

    # 4. — Différentiel
    active = [d for d in analysis.differentials if not d.excluded]
    if active:
        lines.append("DIFFÉRENTIEL PRIORISÉ (règles déterministes) :")
        for d in active:
            meta = DISEASES.get(d.disease)
            label = meta.label_fr if meta else d.label_fr
            pct = int(round(d.score * 100))
            top_notes = d.notes[:1]
            note = f" — {top_notes[0]}" if top_notes else ""
            lines.append(f"{d.rank}. {label} (indice de suspicion {pct} %){note}")
    excluded = [d for d in analysis.differentials if d.excluded]
    for d in excluded:
        if d.exclusion_reason:
            lines.append(f"Écarté : {d.label_fr} ({d.exclusion_reason}).")

    # 5. — Tests requis
    if analysis.rules.required_tests:
        lines.append("EXAMENS RECOMMANDÉS : " +
                     ", ".join(sorted({t.test_code for t in analysis.rules.required_tests})) + ".")

    # 6. — Contraintes thérapeutiques
    forbidden = [dc for dc in analysis.rules.drug_constraints if dc.forbidden]
    allowed = [dc for dc in analysis.rules.drug_constraints if not dc.forbidden]
    if forbidden:
        lines.append("CONTRE-INDICATIONS ACTIVES :")
        for dc in forbidden:
            lines.append(f"• {dc.drug} : {dc.reason}")
    if allowed:
        for dc in allowed:
            lines.append(f"Recommandé : {dc.drug} — {dc.reason}")

    # 7. — Notifications
    if analysis.rules.notifications:
        for n in analysis.rules.notifications:
            lines.append(f"NOTIFICATION : {n['reason']}")

    # 8. — Preuves
    if not pack.empty():
        lines.append(f"BASE DE PREUVES : {pack.summary()}.")
    else:
        lines.append("BASE DE PREUVES : aucune source retrouvée pour cette requête.")

    # 9. — Incertitude
    if analysis.uncertainty.get("reasons"):
        lines.append("Limites : " + "; ".join(analysis.uncertainty["reasons"]) + ".")

    return "\n".join(lines)
