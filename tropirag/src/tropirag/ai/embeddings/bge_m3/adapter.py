"""Adapter BGE-M3 — vecteur depuis n'importe quelle gateway."""
from __future__ import annotations

from tropirag.ai.gateways.deterministic_gateway import hash_embedding


def parse_embedding(resp, text: str, dim_fallback: int = 256) -> list[float]:
    if resp.ok and resp.structured and "embedding" in resp.structured:
        return resp.structured["embedding"]
    return hash_embedding(text, dim_fallback)
