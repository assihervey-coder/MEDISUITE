"""Gateway vLLM — API OpenAI-compatible (http://localhost:8001/v1)."""
from __future__ import annotations

import json
import time

from tropirag.ai.gateways.inference_gateway import InferenceRequest, InferenceResponse


class VLLMGateway:
    """Backend vLLM (completions + embeddings)."""

    name = "vllm"

    def __init__(self, base_url: str = "http://localhost:8001",
                 timeout_s: float = 90.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self._client = None

    def _get_client(self):
        if self._client is None:
            import httpx

            self._client = httpx.Client(timeout=self.timeout_s)
        return self._client

    def is_available(self, model_id: str) -> bool:
        try:
            r = self._get_client().get(f"{self.base_url}/v1/models", timeout=3.0)
            if r.status_code != 200:
                return False
            models = {m.get("id", "") for m in r.json().get("data", [])}
            return any(m.startswith(model_id) for m in models)
        except Exception:  # noqa: BLE001
            return False

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        t0 = time.perf_counter()
        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        content = request.prompt
        if request.images:  # vision : messages multimodaux
            image_url = {"url": f"data:image/jpeg;base64,{request.images[0]}"}
            content = [{"type": "text", "text": request.prompt},
                       {"type": "image_url", "image_url": image_url}]
        messages.append({"role": "user", "content": content})
        payload = {
            "model": request.model_id,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": False,
        }
        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}
        try:
            r = self._get_client().post(f"{self.base_url}/v1/chat/completions",
                                       json=payload, timeout=request.timeout_s)
            latency = (time.perf_counter() - t0) * 1000
            if r.status_code != 200:
                return InferenceResponse(model_id=request.model_id, ok=False,
                                         gateway=self.name, latency_ms=latency,
                                         error=f"HTTP {r.status_code}: {r.text[:200]}")
            data = r.json()
            text = data["choices"][0]["message"]["content"].strip()
            structured = None
            if request.json_mode and text:
                try:
                    structured = json.loads(text)
                except json.JSONDecodeError:
                    structured = None
            usage = data.get("usage", {})
            return InferenceResponse(
                model_id=request.model_id, text=text, structured=structured,
                ok=bool(text), gateway=self.name, latency_ms=latency,
                tokens_in=usage.get("prompt_tokens"),
                tokens_out=usage.get("completion_tokens"),
            )
        except Exception as e:  # noqa: BLE001
            return InferenceResponse(model_id=request.model_id, ok=False,
                                     gateway=self.name, error=str(e))
