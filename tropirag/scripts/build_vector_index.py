#!/usr/bin/env python3
"""Construit l'index vectoriel (hashing déterministe) et le persiste."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.core.config import CORPUS_DIR, DATA_DIR  # noqa: E402
from tropirag.evidence_engine.evidence_engine import load_corpus  # noqa: E402
from tropirag.evidence_engine.retrieval.vector_retriever import VectorIndex  # noqa: E402


def main() -> int:
    units = load_corpus(CORPUS_DIR / "evidence_units")
    vi = VectorIndex(dim=256)
    vi.build(units)
    out = DATA_DIR / "indexes" / "vectors" / "snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "dim": vi.dim, "count": vi.size(),
        "entries": [e.unit_id for e in vi._entries],
    }, ensure_ascii=False))
    print(f"Index vectoriel : {vi.size()} vecteurs (dim {vi.dim}) → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
