"""Client BGE-M3 — sensory retrieval layer."""
from __future__ import annotations

from tropirag.ai.model_client_base import ModelClientBase


class BGEM3Client(ModelClientBase):
    """BGE-M3 : embeddings hybrides (dense) pour le retrieval multicritère."""

    capability = "embeddings"
    default_model_id = "bge-m3"
    temperature = 0.0

    def embed(self, text: str, language: str = "fr") -> "object":
        return self._run(text, language=language)
