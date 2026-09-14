"""Client Qwen Reranker — TOP 30 → TOP 5."""
from __future__ import annotations

from tropirag.ai.model_client_base import ModelClientBase


class QwenRerankerClient(ModelClientBase):
    """Qwen Reranker : reranking cross-encoder du pool hybride."""

    capability = "reranking"
    default_model_id = "qwen-reranker"
    temperature = 0.0

    def rerank(self, query: str, documents: list[str]) -> "object":
        payload = "\n§\n".join(documents)
        return self._run(payload, system=query, language="fr")
