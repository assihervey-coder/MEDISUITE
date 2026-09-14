#!/usr/bin/env python3
"""Construit et persiste l'index BM25 (snapshot JSON des postings)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.core.config import CORPUS_DIR, DATA_DIR  # noqa: E402
from tropirag.evidence_engine.evidence_engine import load_corpus  # noqa: E402
from tropirag.evidence_engine.retrieval.bm25_retriever import BM25Index  # noqa: E402


def main() -> int:
    units = load_corpus(CORPUS_DIR / "evidence_units")
    bm25 = BM25Index()
    bm25.build(units)
    out = DATA_DIR / "indexes" / "bm25" / "snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "size": bm25.size(),
        "avg_len": bm25._avg_len,
        "df": dict(bm25._df),
    }, ensure_ascii=False))
    probe = bm25.search("paludisme fièvre", 3)
    print(f"Index BM25 : {bm25.size()} docs | probe: {probe[:2]} | snapshot → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
