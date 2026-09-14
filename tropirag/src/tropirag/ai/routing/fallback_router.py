"""Fallback Router — chaîne de repli garantie.

local → serveur → déterministe. La chaîne descend JUSQU'AU DÉTERMINISTE :
TropiRAG répond toujours, quitte à répondre « règles uniquement ».
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FallbackChain:
    chain: list[str] = field(default_factory=list)
    chosen: str = "deterministic"
    reason: str = ""


def build_fallback_chain(preferred: str, available: set[str]) -> FallbackChain:
    chain = [preferred] if preferred else []
    if preferred == "deterministic":
        return FallbackChain(["deterministic"], "deterministic", "Mode déterministe natif")
    if preferred not in available:
        chain.append("deterministic")
        return FallbackChain(chain, "deterministic",
                             f"{preferred} indisponible — repli déterministe")
    return FallbackChain(chain, preferred, f"{preferred} disponible")
