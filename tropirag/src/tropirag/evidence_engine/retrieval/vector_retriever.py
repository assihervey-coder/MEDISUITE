"""Retriever vectoriel — embeddings via gateway (BGE-M3) ou hashing déterministe."""
from __future__ import annotations

import math
from dataclasses import dataclass

from tropirag.ai.gateways.deterministic_gateway import hash_embedding
from tropirag.domain.evidence.entities import EvidenceUnit


@dataclass(slots=True)
class _Entry:
    unit_id: str
    vector: list[float]


def _cosine(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    num = sum(x * y for x, y in zip(a[:n], b[:n]))
    da = math.sqrt(sum(x * x for x in a[:n])) or 1.0
    db = math.sqrt(sum(y * y for y in b[:n])) or 1.0
    return num / (da * db)


class VectorIndex:
    """Index vectoriel en mémoire (V1 : corpus embarqué de petite taille)."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self._entries: list[_Entry] = []

    def build(self, units: list[EvidenceUnit], embed_fn=None) -> None:
        """embed_fn(text) -> vector ; par défaut hashing déterministe."""
        self._entries.clear()
        for u in units:
            text = f"{u.source.title} {u.section or ''} {u.text}"
            if embed_fn is not None:
                vec = embed_fn(text)
                if len(vec) < self.dim:
                    vec = (vec + [0.0] * self.dim)[:self.dim]
            else:
                vec = hash_embedding(text, self.dim)
            self._entries.append(_Entry(u.unit_id, vec))

    def search(self, query: str, top_k: int = 30, embed_fn=None) -> list[tuple[str, float]]:
        if not self._entries:
            return []
        if embed_fn is not None:
            qv = embed_fn(query)
            if len(qv) < self.dim:
                qv = (qv + [0.0] * self.dim)[:self.dim]
        else:
            qv = hash_embedding(query, self.dim)
        scored = [(e.unit_id, _cosine(qv, e.vector)) for e in self._entries]
        scored = [(uid, s) for uid, s in scored if s > 0]
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored[:top_k]

    def size(self) -> int:
        return len(self._entries)

    # --- persistance (reconstruction offline instantanée) -----------------
    def save(self, path) -> None:
        """Sérialise les vecteurs (hashing déterministe) en JSON."""
        import json
        from pathlib import Path

        payload = {
            "dim": self.dim,
            "entries": [{"unit_id": e.unit_id, "vector": e.vector}
                        for e in self._entries],
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)

    def load(self, path) -> bool:
        """Restaure les vecteurs — True si chargement réussi."""
        import json
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            return False
        try:
            with open(p, encoding="utf-8") as fh:
                payload = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return False
        dim = int(payload.get("dim", self.dim))
        if dim != self.dim:
            return False  # dimension incompatible → reconstruction
        self._entries = [_Entry(e["unit_id"], [float(x) for x in e["vector"]])
                         for e in payload.get("entries", [])]
        return True
