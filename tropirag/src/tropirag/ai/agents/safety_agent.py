"""Safety Agent — exécute les contrôles déterministes de sécurité du mesh."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent
from tropirag.ai.guards.output_guard import OutputGuard, GuardResult
from tropirag.domain.evidence.entities import EvidencePack


class SafetyAgent(BaseAgent):
    """Applique InputGuard/OutputGuard et les invariants de gouvernance."""

    name = "safety_agent"
    mission = "Garde d'entrée, garde de sortie, invariants — autorité finale."

    def __init__(self, *args: Any, **kw: Any) -> None:
        super().__init__(*args, **kw)
        self.input_guard = None
        self.output_guard = OutputGuard()

    def _execute(self, report: AgentReport, text: str = "",
                 pack: EvidencePack | None = None, mode: str = "output",
                 language: str = "fr", **kwargs: Any) -> None:
        if mode == "input":
            from tropirag.ai.guards.output_guard import InputGuard

            g = GuardResult
            g = InputGuard().check(text)
            report.output = {"guard": "input", "passed": g.passed, "message": g.message}
            report.status = "ok" if g.passed else "failed"
            if not g.passed:
                report.notes.append(g.message)
            return
        # mode output
        if pack is None:
            self._mark(report, "failed", "pas de pack — garde de sortie impossible")
            return
        g = self.output_guard.check(text, pack, language=language)
        report.output = {"guard": "output", "passed": g.passed, "message": g.message,
                         "findings": g.findings}
        report.status = "ok" if g.passed else "failed"
        if not g.passed:
            report.notes.append(f"REFUS : {g.message}")
