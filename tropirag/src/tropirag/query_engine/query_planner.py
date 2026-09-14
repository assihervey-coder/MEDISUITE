"""Query Planner — orchestre l'analyse et construit la requête finale."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.clinical_engine.orchestrator import ClinicalAnalysis
from tropirag.query_engine.clinical_query_builder import build_disease_focus, build_query
from tropirag.query_engine.query_analyzer import QueryAnalysis, analyze_query
from tropirag.query_engine.query_expansion import expand


@dataclass(slots=True)
class QueryPlan:
    analysis: QueryAnalysis
    retrieval_query: str
    disease_focus: list[str] = field(default_factory=list)


class QueryPlanner:

    def plan(self, clinical: ClinicalAnalysis, user_question: str = "") -> QueryPlan:
        qa = analyze_query(user_question or clinical.case.free_text or "fièvre voyage")
        base = build_query(clinical, qa)
        return QueryPlan(analysis=qa,
                          retrieval_query=expand(base),
                          disease_focus=build_disease_focus(clinical))
