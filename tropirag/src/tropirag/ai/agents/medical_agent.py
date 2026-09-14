"""Medical Agent — synthèse clinique encadrée (Med42 via contrat de preuves)."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent
from tropirag.ai.text.med42.client import Med42Client
from tropirag.ai.text.med42.adapter import parse_synthesis


class MedicalAgent(BaseAgent):
    """Produit un PROJET de synthèse clinique — jamais la réponse finale.

    Le projet passe ensuite par l'audit (ReasoningEngine) et le Safety Gate.
    Si l'IA est indisponible : status=degraded, le ResponseEngine prend le relais.
    """

    name = "medical_agent"
    mission = "Projet de synthèse clinique sourcé (contrat : citations obligatoires)."

    def __init__(self, *args: Any, **kw: Any) -> None:
        super().__init__(*args, **kw)
        self._client: Med42Client | None = None

    def _execute(self, report: AgentReport, clinical_context: str = "",
                 evidence_text: str = "", constraints: list[str] | None = None,
                 language: str = "fr", **kwargs: Any) -> None:
        if not self._ai_available() or self.gateways is None:
            self._mark(report, "skipped",
                       "IA indisponible (mode déterministe) — synthèse heuristique par ResponseEngine")
            return
        if not evidence_text.strip():
            self._mark(report, "skipped", "aucune preuve → synthèse IA interdite (invariant)")
            return
        if self._client is None:
            self._client = Med42Client(self.registry, self.router, self.gateways)
        resp = self._client.clinical_synthesis(
            clinical_context=clinical_context,
            evidence_text=evidence_text,
            constraints=constraints or [],
            language=language,
        )
        if not resp.ok:
            self._mark(report, "degraded", f"inférence échouée : {resp.error}")
            return
        parsed = parse_synthesis(resp.structured)
        if not parsed["parse_ok"]:
            self._mark(report, "degraded", "sortie non parsable en JSON — rejetée")
            return
        report.output = {"synthesis": parsed, "raw": resp.text[:4000],
                         "model": resp.model_id, "gateway": resp.gateway}
        report.models_used = [resp.model_id]
        report.status = "ok"
