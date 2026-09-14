"""Synthesis Agent — assemble la réponse finale à partir des rapports validés."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent


class SynthesisAgent(BaseAgent):
    """Assembleur final : ne produit aucun contenu clinique de sa main.

    Il consolide les sorties VALIDÉES des autres agents (synthèse Med42
    passée par l'audit + garde, ou synthèse heuristique déterministe).
    """

    name = "synthesis_agent"
    mission = "Consolidation des rapports validés — zéro création clinique."

    def _execute(self, report: AgentReport, sections: dict[str, Any] | None = None,
                 **kwargs: Any) -> None:
        report.output = {"sections": sections or {}}
        report.status = "ok" if sections else "skipped"
