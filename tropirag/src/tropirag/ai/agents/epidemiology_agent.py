"""Epidemiology Agent — contexte épidémique géographique."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent
from tropirag.domain.travel.geography import risk_level, COUNTRY_NAMES_FR


class EpidemiologyAgent(BaseAgent):
    """Contexte géo-épidémique déterministe par pays visités."""

    name = "epidemiology_agent"
    mission = "Risques par pays (palu/dengue/YF/MVH) + alertes zone."

    def _execute(self, report: AgentReport, countries: list[str] | None = None,
                 **kwargs: Any) -> None:
        profiles: list[dict] = []
        for c in countries or []:
            profiles.append({
                "country": c, "name_fr": COUNTRY_NAMES_FR.get(c, c),
                "malaria": risk_level(c, "malaria"),
                "dengue": risk_level(c, "dengue"),
                "yellow_fever": risk_level(c, "yellow_fever"),
                "lassa": risk_level(c, "lassa"),
                "ebola": risk_level(c, "ebola"),
            })
        report.output = {"profiles": profiles}
        report.status = "ok" if profiles else "skipped"
