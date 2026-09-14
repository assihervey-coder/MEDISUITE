"""Retriever hybride — BM25 + vectoriel, fusion Reciprocal Rank Fusion (RRF).

Chaîne TropiRAG (conforme à l'architecture cible) :

    QUERY → BM25 + BGE-M3 → TOP 30–50 → Reranker → TOP 5 → Evidence Pack
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.domain.evidence.entities import EvidencePack, EvidenceUnit
from tropirag.evidence_engine.retrieval.bm25_retriever import BM25Index
from tropirag.evidence_engine.retrieval.vector_retriever import VectorIndex
from tropirag.evidence_engine.retrieval.metadata_filter import MetadataFilter


@dataclass(slots=True)
class HybridResult:
    unit_id: str
    rrf_score: float
    bm25_rank: int | None = None
    vector_rank: int | None = None
    rerank_score: float | None = None
    final_rank: int = 0


class HybridRetriever:
    """Fusion RRF (k=60) de deux listes de ranking + reranking optionnel."""

    def __init__(self, bm25: BM25Index, vectors: VectorIndex, k: int = 60) -> None:
        self.bm25 = bm25
        self.vectors = vectors
        self.rrf_k = k
        self.units: dict[str, EvidenceUnit] = {}
        self.metadata_filter = MetadataFilter()

    # ------------------------------------------------------------------
    def index(self, units: list[EvidenceUnit], embed_fn=None) -> None:
        self.units = {u.unit_id: u for u in units}
        self.bm25.build(units)
        self.vectors.build(units, embed_fn)

    def retrieve(self, query: str, top_k: int = 30, candidates_per_channel: int = 30,
                 diseases: list[str] | None = None,
                 jurisdiction: str | None = None,
                 embed_fn=None) -> list[HybridResult]:
        """Récupération hybride avec filtrage métadonnées puis fusion RRF."""
        # 1) pool éligible (filtre maladies/juridiction si fournis)
        pool_ids = set(self.units.keys())
        if diseases:
            pool_ids = {uid for uid, u in self.units.items()
                        if u.diseases and (set(u.diseases) & set(diseases))} or pool_ids
        # 2) canaux
        bm25_hits = [(uid, s) for uid, s in self.bm25.search(query, candidates_per_channel)
                     if uid in pool_ids]
        vec_hits = [(uid, s) for uid, s in self.vectors.search(query, candidates_per_channel, embed_fn)
                    if uid in pool_ids]
        # 3) fusion RRF
        scores: dict[str, float] = {}
        bm25_rank: dict[str, int] = {}
        vec_rank: dict[str, int] = {}
        for rank, (uid, _) in enumerate(bm25_hits, 1):
            scores[uid] = scores.get(uid, 0.0) + 1.0 / (self.rrf_k + rank)
            bm25_rank[uid] = rank
        for rank, (uid, _) in enumerate(vec_hits, 1):
            scores[uid] = scores.get(uid, 0.0) + 1.0 / (self.rrf_k + rank)
            vec_rank[uid] = rank
        results = sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:top_k]
        return [HybridResult(unit_id=uid, rrf_score=s,
                              bm25_rank=bm25_rank.get(uid), vector_rank=vec_rank.get(uid))
                for uid, s in results]

    def to_pack(self, query: str, results: list[HybridResult],
                mode: str = "hybrid_deterministic",
                total_candidates: int = 0) -> EvidencePack:
        pack = EvidencePack(query=query, retrieval_mode=mode, total_candidates=total_candidates)
        for r in results:
            u = self.units.get(r.unit_id)
            if u:
                pack.units.append(u)
                pack.scores[u.unit_id] = round(r.rrf_score + (r.rerank_score or 0.0), 4)
        return pack
