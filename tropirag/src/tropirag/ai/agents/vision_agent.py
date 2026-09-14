"""Vision Agent — analyse d'image médicale contextualisée."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent
from tropirag.ai.vision.medgemma.client import MedGemmaClient
from tropirag.ai.vision.medgemma.adapter import parse_vision
from tropirag.ai.vision.minicpm.client import MiniCPMClient
from tropirag.ai.vision.minicpm.adapter import parse_triage


class VisionAgent(BaseAgent):
    """MedGemma (analyse) puis MiniCPM (triage) — deux avis, aucun diagnostic."""

    name = "vision_agent"
    mission = "Observations structurées d'images médicales, jamais de diagnostic."

    def _execute(self, report: AgentReport, image_b64: str = "",
                 clinical_context: str = "", language: str = "fr", **kwargs: Any) -> None:
        if not image_b64:
            self._mark(report, "skipped", "aucune image fournie")
            return
        if not self._ai_available() or self.gateways is None:
            self._mark(report, "skipped", "IA vision indisponible en mode déterministe")
            return
        out: dict[str, Any] = {}
        mg = MedGemmaClient(self.registry, self.router, self.gateways)
        r1 = mg.analyze_image(image_b64, clinical_context, language)
        if r1.ok:
            out["medgemma"] = parse_vision(r1.structured)
            report.models_used.append(r1.model_id)
        else:
            report.notes.append(f"medgemma: {r1.error}")
        mc = MiniCPMClient(self.registry, self.router, self.gateways)
        r2 = mc.triage_image(image_b64, language)
        if r2.ok:
            out["minicpm_triage"] = parse_triage(r2.structured)
            report.models_used.append(r2.model_id)
        else:
            report.notes.append(f"minicpm: {r2.error}")
        if out:
            report.output = out
            report.status = "ok" if "medgemma" in out else "degraded"
        else:
            report.status = "degraded"
            report.notes.append("aucun modèle vision disponible")
