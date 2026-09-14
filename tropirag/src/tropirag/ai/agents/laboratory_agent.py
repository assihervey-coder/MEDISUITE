"""Laboratory Agent — interprétation déterministe des résultats biologiques."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent
from tropirag.domain.diagnostics.results import TestResult
from tropirag.domain.diagnostics.interpretation import interpret
from tropirag.core.constants import (
    SEVERE_ANEMIA_HB, MODERATE_ANEMIA_HB, THROMBOCYTOPENIA_PLT,
    SEVERE_THROMBOCYTOPENIA_PLT, LEUKOPENIA_WBC,
)


class LaboratoryAgent(BaseAgent):
    """Aucune IA : interprétation par seuils déterministes cités."""

    name = "laboratory_agent"
    mission = "Anomalies biologiques par seuils (OMS/MSF) — jamais d'extrapolation."

    def _execute(self, report: AgentReport, lab_results: list[TestResult] | None = None,
                 **kwargs: Any) -> None:
        anomalies: list[dict] = []
        for t in lab_results or []:
            for note in interpret(t):
                anomalies.append({"test": t.test_code, "note": note,
                                  "value": t.numeric, "unit": t.unit})
        # contrôles directs par composants
        report.output = {"anomalies": anomalies,
                         "thresholds": {"hb_severe": SEVERE_ANEMIA_HB,
                                        "hb_moderate": MODERATE_ANEMIA_HB,
                                        "plt": THROMBOCYTOPENIA_PLT,
                                        "plt_severe": SEVERE_THROMBOCYTOPENIA_PLT,
                                        "wbc_low": LEUKOPENIA_WBC}}
        report.status = "ok"
        if not anomalies:
            report.notes.append("aucune anomalie détectée sur les résultats fournis")
