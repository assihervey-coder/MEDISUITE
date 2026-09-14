#!/usr/bin/env python3
"""Ingestion du corpus : unités de preuve → base + index en mémoire → stats."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.evidence_engine.evidence_engine import load_corpus  # noqa: E402
from tropirag.core.config import CORPUS_DIR  # noqa: E402


def main() -> int:
    units = load_corpus(CORPUS_DIR / "evidence_units")
    print(f"Corpus ingéré : {len(units)} unités de preuve")
    from collections import Counter

    by_auth = Counter(u.source.authority.value for u in units)
    for k, v in by_auth.most_common():
        print(f"  {k:15s} {v:3d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
