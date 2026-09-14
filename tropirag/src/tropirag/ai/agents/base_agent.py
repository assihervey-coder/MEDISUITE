"""Agent de base — cycle de vie commun et règles d'or du mesh.

Règles d'or (héritées par TOUS les agents) :
    1. Un agent ne diagnostique JAMAIS de sa propre autorité.
    2. Un agent ne publie que via le Safety Gate.
    3. Un agent cite ses preuves.
    4. Un agent peut échouer — le pipeline déterministe continue.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tropirag.core.identifiers import new_id
from tropirag.ai.gateways.inference_gateway import GatewayManager
from tropirag.ai.registry.model_registry import ModelRegistry
from tropirag.ai.routing.model_router import ModelRouter


@dataclass(slots=True)
class AgentReport:
    agent: str
    task: str
    status: str = "ok"           # ok | degraded | failed | skipped
    output: dict[str, Any] = field(default_factory=dict)
    models_used: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"agent": self.agent, "task": self.task, "status": self.status,
                "models_used": self.models_used, "notes": self.notes,
                "output": self.output}


class BaseAgent:
    """Cycle commun : nom, capacités, exécution protégée, rapport."""

    name: str = "base"
    mission: str = ""

    def __init__(self, router: ModelRouter | None = None,
                 gateways: GatewayManager | None = None,
                 registry: ModelRegistry | None = None) -> None:
        self.router = router
        self.gateways = gateways
        self.registry = registry

    def bind(self, router: ModelRouter, gateways: GatewayManager,
             registry: ModelRegistry | None = None) -> "BaseAgent":
        self.router, self.gateways, self.registry = router, gateways, registry or self.registry
        return self

    # ------------------------------------------------------------------
    def run(self, **kwargs: Any) -> AgentReport:
        """Exécution protégée : toute exception devient un rapport degraded/failed."""
        report = AgentReport(agent=self.name, task=kwargs.get("task", self.name))
        try:
            self._execute(report, **kwargs)
            if report.status == "ok" and not report.notes:
                report.status = "ok"
        except Exception as e:  # noqa: BLE001 — un agent ne casse jamais le pipeline
            report.status = "failed"
            report.notes.append(f"exception: {e}")
        return report

    def _execute(self, report: AgentReport, **kwargs: Any) -> None:  # override
        raise NotImplementedError

    # ------------------------------------------------------------------
    def _ai_available(self) -> bool:
        return self.router is not None and self.router.is_ai_available()

    def _mark(self, report: AgentReport, status: str, note: str) -> None:
        report.status = status
        report.notes.append(note)
