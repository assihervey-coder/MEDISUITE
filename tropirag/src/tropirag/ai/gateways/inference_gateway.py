"""Inference Gateway — interface unique vers les backends d'inférence.

Toutes les requêtes IA passent par une gateway. Les adapters de modèles
(clients) ne voient JAMAIS les backends directement.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from tropirag.core.errors import ModelUnavailableError
from tropirag.ai.registry.model_health import ModelHealthMonitor


@dataclass(slots=True)
class InferenceRequest:
    """Requête générique d'inférence."""

    model_id: str
    task: str                      # étape clinique (ClinicalTask value ou nom de step)
    prompt: str
    system: str | None = None
    images: list[str] = field(default_factory=list)   # chemins ou base64
    audio: str | None = None        # chemin/base64
    temperature: float = 0.1       # basse température = base clinique
    max_tokens: int = 2048
    language: str = "fr"
    json_mode: bool = False
    timeout_s: float = 60.0


@dataclass(slots=True)
class InferenceResponse:
    """Réponse normalisée de n'importe quelle gateway."""

    model_id: str
    text: str = ""
    structured: dict | None = None
    ok: bool = True
    gateway: str = "deterministic"
    latency_ms: float = 0.0
    error: str | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None

    def unwrap(self) -> str:
        if not self.ok:
            raise ModelUnavailableError(self.error or f"Échec {self.model_id}")
        return self.text


class InferenceGateway(Protocol):
    """Contrat de toute gateway."""

    name: str

    def is_available(self, model_id: str) -> bool: ...

    def infer(self, request: InferenceRequest) -> InferenceResponse: ...


class GatewayManager:
    """Maintient les gateways actives et applique la chaîne de repli."""

    def __init__(self, gateways: list[InferenceGateway],
                 health: ModelHealthMonitor | None = None) -> None:
        self._gateways = {g.name: g for g in gateways}
        self.health = health or ModelHealthMonitor()

    def gateway(self, name: str) -> InferenceGateway | None:
        return self._gateways.get(name)

    def execute(self, request: InferenceRequest, preferred: str) -> InferenceResponse:
        """Exécute via la gateway préférée, replie sur le déterministe."""
        order = [preferred, "deterministic"]
        last: InferenceResponse | None = None
        for name in order:
            gw = self._gateways.get(name)
            if gw is None:
                continue
            if not gw.is_available(request.model_id):
                continue
            try:
                resp = gw.infer(request)
            except Exception as e:  # noqa: BLE001 — la gateway ne doit jamais casser le pipeline
                self.health.report_failure(request.model_id, str(e))
                last = InferenceResponse(model_id=request.model_id, ok=False,
                                         gateway=name, error=str(e))
                continue
            if resp.ok:
                self.health.report_success(request.model_id, resp.latency_ms)
                return resp
            self.health.report_failure(request.model_id, resp.error or "échec inconnu")
            last = resp
        if last is not None:
            return last
        return InferenceResponse(model_id=request.model_id, ok=False,
                                 gateway="none", error="Aucune gateway disponible")
