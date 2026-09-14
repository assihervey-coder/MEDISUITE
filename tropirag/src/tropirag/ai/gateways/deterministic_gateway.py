"""Gateway déterministe — repli algorithmique garanti SANS AUCUN modèle IA.

Capacités réellement fournies (algorithmes purs, reproductibles) :
    - embeddings : hashing n-grammes stable (compatible BGE-M3 interface)
    - reranking  : reranker lexical pondéré (recouvrement + autorité source)

Capacités refusées proprement (aucun modèle embarqué) :
    - texte génératif, vision, voix → ok=False, le pipeline replie sur
      les heuristiques déterministes du ResponseEngine.
"""
from __future__ import annotations

import math
import re
import time
import unicodedata
from collections import Counter

from tropirag.ai.gateways.inference_gateway import InferenceRequest, InferenceResponse

_DIM = 256


def _normalize(text: str) -> str:
    t = unicodedata.normalize("NFKD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def _tokens(text: str) -> list[str]:
    return [t for t in _normalize(text).split() if len(t) > 2]


def _ngrams(text: str, n: int = 2) -> list[str]:
    toks = _tokens(text)
    return toks + [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]


def _stable_hash(s: str, salt: int = 0) -> int:
    """Hash déterministe (FNV-1a salé) — même texte → même vecteur, partout."""
    h = 2166136261 ^ salt
    for byte in s.encode("utf-8"):
        h ^= byte
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def hash_embedding(text: str, dim: int = _DIM) -> list[float]:
    """Embedding déterministe par hashing-trick + pondération TF-IDF-like."""
    vec = [0.0] * dim
    grams = _ngrams(text)
    if not grams:
        return vec
    counts = Counter(grams)
    for gram, tf in counts.items():
        idx = _stable_hash(gram) % dim
        sign = 1.0 if _stable_hash(gram, salt=7) % 2 == 0 else -1.0
        weight = 1.0 + math.log(tf)
        vec[idx] += sign * weight
    # normalisation L2
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / norm, 6) for v in vec]


def lexical_overlap_score(query: str, text: str) -> float:
    """Score de recouvrement lexical pondéré (0–1) — reranking déterministe."""
    q = set(_tokens(query)) | set(_ngrams(query, 2))
    t = set(_tokens(text)) | set(_ngrams(text, 2))
    if not q or not t:
        return 0.0
    inter = q & t
    return len(inter) / (len(q) ** 0.5 * len(t) ** 0.5)


class DeterministicGateway:
    """Gateway algorithmique — toujours disponible, cliniquement muette."""

    name = "deterministic"

    def __init__(self, dim: int = _DIM) -> None:
        self.dim = dim

    def is_available(self, model_id: str) -> bool:
        return model_id in ("bge-m3", "qwen-reranker", "deterministic-lex")

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        t0 = time.perf_counter()
        task = request.task
        if task == "embeddings" or task == "embed":
            vec = hash_embedding(request.prompt, self.dim)
            return InferenceResponse(
                model_id=request.model_id, text="", ok=True, gateway=self.name,
                latency_ms=(time.perf_counter() - t0) * 1000,
                structured={"embedding": vec, "dim": self.dim},
            )
        if task == "reranking" or task == "rerank":
            texts = request.prompt.split("\n§\n") if "§" in request.prompt else [request.prompt]
            scores = [round(lexical_overlap_score(request.system or "", t), 4) for t in texts]
            return InferenceResponse(
                model_id=request.model_id, text="", ok=True, gateway=self.name,
                latency_ms=(time.perf_counter() - t0) * 1000,
                structured={"scores": scores},
            )
        # capacité générative/analytique non émulable sans modèle
        return InferenceResponse(
            model_id=request.model_id, ok=False, gateway=self.name,
            latency_ms=(time.perf_counter() - t0) * 1000,
            error=(f"Mode déterministe : la capacité '{task}' requiert un modèle IA — "
                   f"repli heuristique du ResponseEngine"),
        )
