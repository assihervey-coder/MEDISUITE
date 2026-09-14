"""Base commune des clients de modèles du mesh.

Chaque client :
  1. route sa capacité via le MODEL_ROUTER,
  2. construit sa requête (prompts centralisés),
  3. exécute via une GATEWAY (jamais en direct),
  4. normalise sa réponse.

Les clients ne prennent AUCUNE décision clinique : ils produisent du texte
ou des vecteurs, sous contrat de gouvernance.
"""
from __future__ import annotations

from pathlib import Path

from tropirag.ai.gateways.inference_gateway import (
    GatewayManager,
    InferenceRequest,
    InferenceResponse,
)
from tropirag.ai.registry.model_health import ModelHealthMonitor
from tropirag.ai.registry.model_registry import ModelRegistry
from tropirag.ai.routing.model_router import ModelRouter

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "tropirag" / "ai" / "prompts"


def load_prompt(name: str, subdir: str = "") -> str:
    """Charge un prompt depuis ai/prompts/ (fichier .md)."""
    p = PROMPTS_DIR / subdir / f"{name}.md"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    return ""


class ModelClientBase:
    """Client de modèle — un par modèle du mesh."""

    capability: str = ""            # ClinicalTask value
    default_model_id: str = ""
    temperature: float = 0.1
    max_tokens: int = 2048

    def __init__(self,
                 registry: ModelRegistry | None = None,
                 router: ModelRouter | None = None,
                 gateways: GatewayManager | None = None) -> None:
        self.registry = registry
        self.router = router
        self.gateways = gateways
        self.last_decision = None
        self.last_response: InferenceResponse | None = None

    # --- configuration --------------------------------------------------------
    def bind(self, router: ModelRouter, gateways: GatewayManager,
             registry: ModelRegistry | None = None) -> "ModelClientBase":
        self.router, self.gateways, self.registry = router, gateways, registry or self.registry
        return self

    # --- exécution ------------------------------------------------------------
    def _run(self, prompt: str, *, system: str | None = None, language: str = "fr",
             json_mode: bool = False, images: list[str] | None = None,
             audio: str | None = None, timeout_s: float = 60.0) -> InferenceResponse:
        assert self.router and self.gateways, "client non lié (bind requis)"
        decision = self.router.route(self._task(), language=language)
        self.last_decision = decision
        if decision.selected is None or decision.degraded:
            return InferenceResponse(
                model_id=decision.selected or "none", ok=False,
                gateway="deterministic",
                error=decision.reason,
            )
        model = self.registry.get(decision.selected) if self.registry else None
        preferred_gateway = model.provider_gateway if model else "ollama"
        req = InferenceRequest(
            model_id=decision.selected,
            task=decision.reason and self.capability or self.capability,
            prompt=prompt,
            system=system,
            images=images or [],
            audio=audio,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            language=language,
            json_mode=json_mode,
            timeout_s=timeout_s,
        )
        resp = self.gateways.execute(req, preferred_gateway)
        self.last_response = resp
        return resp

    def _task(self) -> "object":
        from tropirag.core.enums import ClinicalTask

        return ClinicalTask(self.capability)

    # --- introspection ----------------------------------------------------------
    def describe(self) -> dict:
        return {
            "capability": self.capability,
            "default_model": self.default_model_id,
            "last_decision": self.last_decision.to_dict() if self.last_decision else None,
        }
