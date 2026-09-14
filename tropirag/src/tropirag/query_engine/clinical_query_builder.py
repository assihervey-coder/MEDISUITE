"""Constructeur de requête de retrieval — combine cas + intent."""
from __future__ import annotations

from tropirag.clinical_engine.orchestrator import ClinicalAnalysis
from tropirag.domain.symptoms.taxonomy import symptom_label


def build_query(analysis: ClinicalAnalysis, qa) -> str:
    """Requête de retrieval riche : symptômes + voyage + suspicions + question."""
    c = analysis.case
    parts: list[str] = []
    for code in sorted(c.symptom_codes()):
        parts.append(symptom_label(code))
    if c.timeline:
        countries = c.travel.countries_visited()
        if countries:
            parts.append("voyage " + " ".join(countries))
    for d in analysis.differentials[:4]:
        if not d.excluded:
            parts.append(d.label_fr)
    parts.append(qa.raw[:300])
    seen, out = set(), []
    for p in parts:
        if p and p.lower() not in seen:
            seen.add(p.lower())
            out.append(p)
    return " ".join(out)


def build_disease_focus(analysis: ClinicalAnalysis) -> list[str]:
    return [d.disease for d in analysis.differentials if not d.excluded][:5]
