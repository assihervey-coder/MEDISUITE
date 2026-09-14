"""Moteur de différentiel — priorisation déterministe des hypothèses.

Principe : la suspicion vient des règles (poids additionnés), la priorité
vient du danger de rater la maladie (must-not-miss), la cohérence vient
du moteur d'incubation. Aucun score n'est produit par un LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.core.enums import Severity
from tropirag.clinical_engine.rules.rule_executor import RuleExecutionResult
from tropirag.clinical_engine.temporal.incubation_engine import IncubationEngine
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.diseases.entities import DISEASES


@dataclass(slots=True)
class DifferentialEntry:
    disease: str
    label_fr: str
    score: float                  # 0–1 : confiance de suspicion
    rank: int = 0
    must_not_miss: bool = False
    contributing_rules: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    incubation_compatible: bool | None = None
    evidence_refs: list[str] = field(default_factory=list)
    excluded: bool = False
    exclusion_reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "disease": self.disease,
            "label": self.label_fr,
            "score": round(self.score, 3),
            "must_not_miss": self.must_not_miss,
            "notes": self.notes,
            "incubation_compatible": self.incubation_compatible,
            "contributing_rules": self.contributing_rules,
            "evidence_refs": self.evidence_refs,
            "excluded": self.excluded,
            "exclusion_reason": self.exclusion_reason,
        }


class DifferentialEngine:
    """Agrège les suspicions des règles en différentiel ordonné et explicable."""

    def __init__(self, incubation: IncubationEngine | None = None) -> None:
        self._incubation = incubation or IncubationEngine()

    def build(self, case: ClinicalCase, rules: RuleExecutionResult) -> list[DifferentialEntry]:
        # 1) agréger les poids par maladie
        agg: dict[str, DifferentialEntry] = {}
        for s in rules.suspicions:
            e = agg.setdefault(
                s.disease,
                DifferentialEntry(
                    disease=s.disease,
                    label_fr=DISEASES[s.disease].label_fr if s.disease in DISEASES else s.disease,
                    score=0.0,
                    must_not_miss=DISEASES[s.disease].must_not_miss if s.disease in DISEASES else False,
                    evidence_refs=list(DISEASES[s.disease].evidence_refs) if s.disease in DISEASES else [],
                ),
            )
            e.score = min(1.0, e.score + s.weight)
            e.contributing_rules.append(s.rule_id)
            if s.note:
                e.notes.append(s.note)

        entries = list(agg.values())

        # 2) cohérence temporelle
        checks = {c.disease: c for c in self._incubation.check_all(case, list(agg.keys()))}
        for e in entries:
            c = checks.get(e.disease)
            if c and not c.compatible and "trop tardif" in c.reason:
                e.excluded = True
                e.exclusion_reason = c.reason
            elif c:
                e.incubation_compatible = c.compatible
                if not c.compatible:
                    e.notes.append(c.reason)

        # 3) tri : score décroissant ; égalité → must_not_miss d'abord ; puis nom
        entries.sort(key=lambda e: (-e.score, not e.must_not_miss, e.disease))

        # 4) rang (les exclusés restent visibles pour l'audit, en fin de liste)
        ranked = [e for e in entries if not e.excluded]
        for i, e in enumerate(ranked, 1):
            e.rank = i
        for i, e in enumerate([x for x in entries if x.excluded], len(ranked) + 1):
            e.rank = i
        return entries


class UncertaintyAssessor:
    """Quantifie l'incertitude résiduelle du différentiel."""

    def assess(self, differentials: list[DifferentialEntry], case: ClinicalCase) -> dict:
        has_top = bool(differentials and not differentials[0].excluded)
        top_score = differentials[0].score if has_top else 0.0
        if not has_top or top_score < 0.2:
            level = "high"
        elif top_score >= 0.6:
            level = "low"
        else:
            level = "moderate"
        reasons: list[str] = []
        if case.timeline is None or case.timeline.anchor.symptom_onset is None:
            reasons.append("date de début des symptômes manquante")
        if not case.lab_results:
            reasons.append("aucun résultat biologique disponible")
        if not case.travel.segments:
            reasons.append("historique de voyage non renseigné")
        return {
            "level": level,
            "top_score": round(top_score, 2),
            "reasons": reasons,
            "statement": (
                "Incertitude forte — collecter davantage de données (voyage, labs, examen)."
                if level == "high"
                else "Incertitude modérée — confirmer par les tests recommandés."
                if level == "moderate"
                else "Hypothèse principale robuste, à confirmer par les tests recommandés."
            ),
        }
