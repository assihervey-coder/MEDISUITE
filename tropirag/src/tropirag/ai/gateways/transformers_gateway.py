"""Gateway Transformers (HuggingFace local) — exécution directe si installé.

Utilisée pour BGE-M3 / reranker hors Ollama. Import paresseux : si
`transformers` n'est pas installé, la gateway se déclare indisponible
et le système replie sur DeterministicGateway.
"""
from __future__ import annotations

import time

from tropirag.ai.gateways.inference_gateway import InferenceRequest, InferenceResponse


class TransformersGateway:

    name = "transformers"

    def __init__(self) -> None:
        self._models: dict[str, object] = {}
        self._available: bool | None = None

    def _check(self) -> bool:
        if self._available is None:
            try:
                import transformers  # noqa: F401

                self._available = True
            except ImportError:
                self._available = False
        return self._available

    def is_available(self, model_id: str) -> bool:
        return self._check()

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        if not self._check():
            return InferenceResponse(model_id=request.model_id, ok=False,
                                     gateway=self.name,
                                     error="transformers non installé")
        t0 = time.perf_counter()
        try:
            from transformers import pipeline as hf_pipeline

            key = request.model_id
            if key not in self._models:
                self._models[key] = hf_pipeline("feature-extraction", model=key)
            vec = self._models[key](request.prompt)[0][0]
            return InferenceResponse(model_id=request.model_id, ok=True,
                                     gateway=self.name,
                                     latency_ms=(time.perf_counter() - t0) * 1000,
                                     structured={"embedding": [float(x) for x in vec]})
        except Exception as e:  # noqa: BLE001
            return InferenceResponse(model_id=request.model_id, ok=False,
                                     gateway=self.name, error=str(e))
