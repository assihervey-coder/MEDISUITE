"""Evidence Engine — charge le corpus, indexe, récupère, reranke, valide.

Chaîne complète (architecture cible) :

    QUERY → [BM25 ∥ BGE-M3] → TOP 30 → Reranker → TOP 5 → Evidence Pack
"""
from __future__ import annotations

import time
from pathlib import Path

import yaml

from tropirag.ai.gateways.inference_gateway import GatewayManager
from tropirag.core.config import CORPUS_DIR, get_config
from tropirag.core.enums import SourceAuthority
from tropirag.domain.evidence.entities import EvidencePack, EvidenceUnit, SourceRef
from tropirag.evidence_engine.reranking.rerank_engine import (
    rerank_deterministic,
    rerank_with_model,
)
from tropirag.evidence_engine.retrieval.bm25_retriever import BM25Index
from tropirag.evidence_engine.retrieval.hybrid_retriever import HybridRetriever
from tropirag.evidence_engine.retrieval.vector_retriever import VectorIndex
from tropirag.evidence_engine.validation.source_validator import SourceValidator
from tropirag.evidence_engine.validation.temporal_validator import TemporalValidator


def load_corpus(corpus_dir: Path | None = None) -> list[EvidenceUnit]:
    """Charge toutes les unités + sources depuis corpus/evidence_units."""
    base = corpus_dir or (CORPUS_DIR / "evidence_units")
    units: list[EvidenceUnit] = []
    sources: dict[str, SourceRef] = {}

    src_cache: dict[str, dict] = {}
    # pré-chargement des sources
    for src_yaml in sorted((CORPUS_DIR / "sources").rglob("*.yaml")):
        with open(src_yaml, encoding="utf-8") as fh:
            meta = yaml.safe_load(fh) or {}
        sid = str(meta.get("source_id") or src_yaml.stem)
        src_cache[sid] = meta

    for uf in sorted(base.glob("*.yaml")):
        if uf.name in ("corpus_manifest.yaml",):
            continue
        with open(uf, encoding="utf-8") as fh:
            d = yaml.safe_load(fh) or {}
        sid = str(d.get("source_id", ""))
        meta = src_cache.get(sid, {})
        if sid not in sources:
            sources[sid] = SourceRef(
                source_id=sid,
                authority=SourceAuthority(meta.get("authority", "unknown")),
                title=str(meta.get("title", sid)),
                publisher=str(meta.get("publisher", sid)),
                edition_date=meta.get("edition_date"),
                url=meta.get("url"),
                jurisdiction=str(meta.get("jurisdiction", "INT")),
            )
        u = EvidenceUnit(
            unit_id=str(d["unit_id"]),
            text=str(d.get("text", "")),
            source=sources[sid],
            section=d.get("section"),
            topics=list(d.get("topics", [])),
            diseases=list(d.get("diseases", [])),
            jurisdiction=str(d.get("jurisdiction", "INT")),
            language=str(d.get("language", "fr")),
        )
        if u.text.strip():
            units.append(u)
    return units


class EvidenceEngine:
    """Point d'entrée unique du RAG TropiRAG."""

    def __init__(self, gateways: GatewayManager | None = None,
                 corpus_dir: Path | None = None) -> None:
        self.cfg = get_config()
        self.units: list[EvidenceUnit] = []
        self._sources_validator = SourceValidator()
        self._temporal_validator = TemporalValidator()
        bm25 = BM25Index(k1=self.cfg.retrieval.bm25_k1, b=self.cfg.retrieval.bm25_b)
        vectors = VectorIndex(dim=self.cfg.retrieval.vector_dimensions)
        self.hybrid = HybridRetriever(bm25, vectors, k=self.cfg.retrieval.fusion_rrf_k)
        self._gateways = gateways
        self._loaded = False

    # ------------------------------------------------------------------
    def load(self, corpus_dir: Path | None = None) -> int:
        self.units = load_corpus(corpus_dir)
        # validation des sources au chargement
        bad = [u.unit_id for u in self.units
               if not self._sources_validator.validate(u).passed]
        self.units = [u for u in self.units if u.unit_id not in bad]
        # embeddings : BGE-M3 si mesh actif, sinon hashing déterministe
        embed_fn = None
        if self._gateways is not None and self._embed_gateway_available():
            from tropirag.ai.gateways.deterministic_gateway import DeterministicGateway  # noqa: F401

            embed_fn = None  # V1 : hashing déterministe partout (reproductible)
        # tentative de restauration d'index persistants (invalidation par hash)
        if not self._try_load_indexes():
            self.hybrid.index(self.units, embed_fn=embed_fn)
            self._save_indexes()
        self._loaded = True
        return len(self.units)

    # --- persistance des index (data/indexes/) -----------------------------
    def _index_dir(self) -> Path:
        from tropirag.core.config import DATA_DIR
        return DATA_DIR / "data" / "indexes"

    def corpus_hash(self) -> str:
        """Empreinte SHA-256 agrégée du corpus chargé (clé d'invalidation)."""
        import hashlib
        h = hashlib.sha256()
        for u in sorted(self.units, key=lambda x: x.unit_id):
            h.update(u.unit_id.encode())
            h.update(u.text.encode())
        return h.hexdigest()

    def _try_load_indexes(self) -> bool:
        """Restaure BM25 + vecteurs si l'empreinte du corpus correspond."""
        import json
        base = self._index_dir()
        meta = base / "index_meta.json"
        try:
            with open(meta, encoding="utf-8") as fh:
                info = json.load(fh)
            if info.get("corpus_sha256") != self.corpus_hash():
                return False  # corpus modifié → reconstruction
            if not self.hybrid.bm25.load(base / "bm25" / "bm25.json"):
                return False
            if not self.hybrid.vectors.load(base / "vectors" / "vectors.json"):
                return False
        except (OSError, json.JSONDecodeError):
            return False
        # le dictionnaire d'unités reste TOUJOURS aligné sur le corpus chargé
        self.hybrid.units = {u.unit_id: u for u in self.units}
        return True

    def _save_indexes(self) -> None:
        import json
        base = self._index_dir()
        try:
            self.hybrid.bm25.save(base / "bm25" / "bm25.json")
            self.hybrid.vectors.save(base / "vectors" / "vectors.json")
            with open(base / "index_meta.json", "w", encoding="utf-8") as fh:
                json.dump({"corpus_sha256": self.corpus_hash(),
                           "units": len(self.units),
                           "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S")}, fh)
        except OSError:
            pass  # l'index persistant est un cache : jamais bloquant

    def _embed_gateway_available(self) -> bool:
        return False  # V1 : reproductibilité absolue — hashing déterministe

    @property
    def loaded(self) -> bool:
        return self._loaded and bool(self.units)

    def size(self) -> int:
        return len(self.units)

    # ------------------------------------------------------------------
    def retrieve_evidence(self, query: str, diseases: list[str] | None = None,
                          jurisdiction: str | None = None,
                          top_k: int | None = None) -> EvidencePack:
        """Retrieval hybride + reranking + validation — renvoie un pack."""
        if not self.loaded:
            self.load()
        top_k = top_k or self.cfg.retrieval.rerank_top_k
        results = self.hybrid.retrieve(query, top_k=top_k * 3,
                                       diseases=diseases or None)
        # pack brut pour rerank
        pack = self.hybrid.to_pack(query, results, total_candidates=len(results))
        # reranking : Qwen si dispo, sinon lexical autorité-pondéré
        reranked = None
        if self._gateways is not None:
            reranked = rerank_with_model(query, pack.units, self._gateways, top_k)
        if reranked is None:
            reranked = rerank_deterministic(query, pack.units)[:top_k]
        # pack final ordonné par score de rerank
        final = EvidencePack(query=query,
                             retrieval_mode="hybrid_rrf+lex_rerank",
                             total_candidates=len(results))
        unit_map = {u.unit_id: u for u in pack.units}
        for uid, score in reranked[:top_k]:
            u = unit_map.get(uid)
            if u is None:
                continue
            # validation temporelle : les unités périmées sont exclues du pack actif
            if not self._temporal_validator.validate(u).passed:
                continue
            final.units.append(u)
            final.scores[uid] = score
        # tri par score de rerank décroissant
        final.units.sort(key=lambda u: final.scores.get(u.unit_id, 0.0), reverse=True)
        return final

    # ------------------------------------------------------------------
    def stats(self) -> dict:
        by_auth: dict[str, int] = {}
        for u in self.units:
            by_auth[u.source.authority.value] = by_auth.get(u.source.authority.value, 0) + 1
        return {"units": len(self.units), "sources_by_authority": by_auth,
                "bm25_size": self.hybrid.bm25.size(),
                "vector_size": self.hybrid.vectors.size()}
