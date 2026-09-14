"""BM25 — implémentation pure Python (aucune dépendance), reproductible.

Corpus de référence TropiRAG (OMS/MSF/CDC) : quelques centaines d'unités,
le BM25 in-memory est le bon compromis V1 (audit, latence, offline).
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

from tropirag.domain.evidence.entities import EvidenceUnit

_WORD_RE = re.compile(r"[a-zàâçéèêëîïôûùüÿñæœ0-9]+")


def tokenize(text: str) -> list[str]:
    t = unicodedata.normalize("NFKD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return [w for w in _WORD_RE.findall(t) if len(w) > 1]


@dataclass(slots=True)
class BM25Doc:
    unit_id: str
    tokens: list[str]
    tf: Counter
    length: int


class BM25Index:
    """BM25 (k1, b classiques) sur les EvidenceUnits."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self._docs: dict[str, BM25Doc] = {}
        self._df: Counter = Counter()
        self._avg_len: float = 0.0
        self._n: int = 0

    # ------------------------------------------------------------------
    def add_unit(self, unit: EvidenceUnit) -> None:
        text = f"{unit.source.title} {unit.section or ''} {unit.text}"
        toks = tokenize(text)
        doc = BM25Doc(unit.unit_id, toks, Counter(toks), len(toks))
        self._docs[unit.unit_id] = doc
        self._n = len(self._docs)
        for term in doc.tf:
            self._df[term] += 1
        self._avg_len = sum(d.length for d in self._docs.values()) / max(1, self._n)

    def build(self, units: list[EvidenceUnit]) -> None:
        self._docs.clear()
        self._df.clear()
        for u in units:
            self.add_unit(u)

    # ------------------------------------------------------------------
    def _idf(self, term: str) -> float:
        df = self._df.get(term, 0)
        return math.log(1.0 + (self._n - df + 0.5) / (df + 0.5)) if df else 0.0

    def score(self, query: str, unit_id: str) -> float:
        doc = self._docs.get(unit_id)
        if not doc:
            return 0.0
        s = 0.0
        for term in tokenize(query):
            f = doc.tf.get(term, 0)
            if not f:
                continue
            idf = self._idf(term)
            denom = f + self.k1 * (1 - self.b + self.b * doc.length / max(1e-9, self._avg_len))
            s += idf * (f * (self.k1 + 1)) / denom
        return s

    def search(self, query: str, top_k: int = 30) -> list[tuple[str, float]]:
        if not self._docs:
            return []
        scored = [(uid, self.score(query, uid)) for uid in self._docs]
        scored = [(uid, s) for uid, s in scored if s > 0]
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored[:top_k]

    def size(self) -> int:
        return len(self._docs)

    # --- persistance (reconstruction offline instantanée) -----------------
    def save(self, path) -> None:
        """Sérialise l'état BM25 (df + tf + longueur) en JSON."""
        import json
        from pathlib import Path

        payload = {
            "k1": self.k1, "b": self.b, "n": self._n, "avg_len": self._avg_len,
            "df": dict(self._df),
            "docs": {
                uid: {"length": d.length, "tf": dict(d.tf)}
                for uid, d in self._docs.items()
            },
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)

    def load(self, path) -> bool:
        """Restaure l'état BM25 — True si chargement réussi."""
        import json
        from collections import Counter
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            return False
        try:
            with open(p, encoding="utf-8") as fh:
                payload = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return False
        self.k1, self.b = payload.get("k1", self.k1), payload.get("b", self.b)
        self._df = Counter(payload.get("df", {}))
        self._docs = {}
        for uid, d in payload.get("docs", {}).items():
            tf = Counter(d.get("tf", {}))
            self._docs[uid] = BM25Doc(uid, list(tf), tf, int(d.get("length", sum(tf.values()))))
        self._n = int(payload.get("n", len(self._docs)))
        self._avg_len = float(payload.get("avg_len", 0.0))
        return True
