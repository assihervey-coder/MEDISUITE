"""Moteur de reranking — lexical déterministe + Qwen (si mesh actif)."""
from __future__ import annotations

from tropirag.ai.gateways.deterministic_gateway import lexical_overlap_score
from tropirag.ai.gateways.inference_gateway import GatewayManager
from tropirag.domain.evidence.entities import EvidenceUnit


def rerank_deterministic(query: str, units: list[EvidenceUnit],
                         boost_authority: bool = True) -> list[tuple[str, float]]:
    """Score = recouvrement lexical (+ bonus autorité de source)."""
    out: list[tuple[str, float]] = []
    for u in units:
        s = lexical_overlap_score(query, f"{u.source.title} {u.section or ''} {u.text}")
        if boost_authority:
            # OMS 1.15x, national/MSF/CDC 1.10x
            auth = u.source.authority.value
            s *= {"who": 1.15, "national": 1.10, "msf": 1.10, "cdc": 1.10}.get(auth, 1.0)
        out.append((u.unit_id, round(s, 4)))
    out.sort(key=lambda x: (-x[1], x[0]))
    return out


def rerank_with_model(query: str, units: list[EvidenceUnit],
                      gateways: GatewayManager | None = None,
                      top_k: int = 5) -> list[tuple[str, float]] | None:
    """Reranking Qwen si disponible — sinon None (fallback lexical)."""
    if gateways is None:
        return None
    from tropirag.ai.gateways.inference_gateway import InferenceRequest

    docs = [f"{u.source.title} {u.text[:300]}" for u in units]
    req = InferenceRequest(model_id="qwen-reranker", task="reranking",
                            prompt="\n§\n".join(docs), system=query)
    for gw_name in ("ollama", "vllm"):
        gw = gateways.gateway(gw_name)
        if gw is None or not gw.is_available("qwen-reranker"):
            continue
        resp = gw.infer(req)
        if resp.ok and resp.structured and "scores" in resp.structured:
            scores = [float(x) for x in resp.structured["scores"]]
            pairs = [(u.unit_id, s) for u, s in zip(units, scores)]
            pairs.sort(key=lambda x: (-x[1], x[0]))
            return pairs[:top_k]
    return None
