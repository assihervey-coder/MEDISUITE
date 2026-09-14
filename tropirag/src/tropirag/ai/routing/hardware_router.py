"""Hardware Router — allocation GPU du mesh (4 nœuds × 8 GPU × 48 Go).

Plan d'allocation V1 (voir docs/architecture/DEPLOYMENT_ARCHITECTURE.md) :
    NŒUD 1 : services  (ASR, embeddings, reranker, vision légère, vector DB)
    NŒUD 2 : raisonnement A (Med42 TP=4, OpenBioLLM TP=4)
    NŒUD 3 : raisonnement B (répliques)
    NŒUD 4 : audit + standby + batch nocturne
"""
from __future__ import annotations

from dataclasses import dataclass

NODE_PLAN: dict[str, str] = {
    "medasr-quantized": "node1",
    "whisper-large-v3": "node1",
    "bge-m3": "node1",
    "qwen-reranker": "node1",
    "medgemma-4b-it": "node1",
    "minicpm-v-2.6": "node1",
    "med42-v2-70b": "node2|node3",
    "openbiollm-70b": "node2|node3",
    "deepseek-r1-distill-32b": "node4",
}


@dataclass(slots=True)
class Placement:
    model_id: str
    nodes: list[str]
    tensor_parallel: int = 1


def placement_for(model_id: str) -> Placement:
    nodes = NODE_PLAN.get(model_id, "node4").split("|")
    tp = 4 if "70b" in model_id else 1
    return Placement(model_id=model_id, nodes=nodes, tensor_parallel=tp)
