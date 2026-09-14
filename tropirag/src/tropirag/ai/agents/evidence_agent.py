"""Evidence Agent — assemblage du pack de preuves RAG."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent
from tropirag.domain.evidence.entities import EvidencePack


class EvidenceAgent(BaseAgent):
    """Recherche, fusion, reranking, assemblage de l'EvidencePack.

    Travaille exclusivement avec des sources authentifiées du corpus
    (OMS/MSF/CDC/national). Aucune génération libre.
    """

    name = "evidence_agent"
    mission = "Assemble l'EvidencePack sourcé pour la requête clinique."

    def _execute(self, report: AgentReport, evidence_engine=None,
                 query: str = "", diseases: list[str] | None = None,
                 **kwargs: Any) -> None:
        if evidence_engine is None:
            self._mark(report, "failed", "evidence_engine non fourni")
            return
        if not query:
            self._mark(report, "skipped", "aucune requête")
            return
        pack: EvidencePack = evidence_engine.retrieve_evidence(
            query=query, diseases=diseases or [])
        report.output = {"pack": pack}
        report.models_used = ["bge-m3", "qwen-reranker"]
        report.status = "ok" if not pack.empty() else "degraded"
        if pack.empty():
            report.notes.append("aucune preuve retrouvée — synthèse IA sera refusée")
        else:
            report.notes.append(pack.summary())
