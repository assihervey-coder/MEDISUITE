#!/usr/bin/env python3
"""Évalue le retrieval : pertinence top-k sur requêtes cliniques de référence."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.evidence_engine.evidence_engine import EvidenceEngine  # noqa: E402

# (requête, unités attendues dans le top 5)
BENCH = [
    ("fièvre voyage zone paludéenne suspicion", ["eu-who-mal-001", "eu-ci-mal-009"]),
    ("dengue signes d'alarme AINS interdits", ["eu-who-den-002", "eu-who-den-003"]),
    ("paludisme sévère artésunate IV critères", ["eu-who-mals-005", "eu-who-mals-006"]),
    ("typhoïde hémoculture diagnostic", ["eu-who-typ-001", "eu-who-typ-002"]),
    ("fièvre jaune ictère vaccination", ["eu-who-yf-001", "eu-who-yf-002"]),
    ("ebola isolement 21 jours épidémie", ["eu-who-vhf-001", "eu-who-vhf-002"]),
    ("méningite ceftriaxone urgence", ["eu-who-men-001"]),
    ("leptospirose eaux stagnantes ictere", ["eu-who-lepto-001"]),
    ("chikungunya arthralgies éruption", ["eu-who-chik-001"]),
    ("zika grossesse microcéphalie", ["eu-who-zik-001"]),
    ("TDR paludisme négatif interprétation", ["eu-who-mal-002"]),
    ("thrombopénie NS1 diagnostic dengue", ["eu-who-den-004"]),
]


def main() -> int:
    ee = EvidenceEngine()
    ee.load()
    hits_at_1, hits_at_5, total = 0, 0, 0
    print("─" * 70)
    print(f"{'requête':44s} top1  top5")
    print("─" * 70)
    for query, expected in BENCH:
        pack = ee.retrieve_evidence(query, top_k=5)
        got = [u.unit_id for u in pack.top(5)]
        exp_hits = [e for e in expected if e in got]
        top1 = "✓" if expected and any(e == got[0] for e in expected[:1]) else "·"
        print(f"{query[:44]:44s}  {top1}    {len(exp_hits)}/{len(expected)}")
        if expected and got and got[0] in expected:
            hits_at_1 += 1
        hits_at_5 += len(exp_hits) == len(expected)
        total += 1
    print("─" * 70)
    p1, p5 = hits_at_1 / total, hits_at_5 / total
    print(f"Précision@1 : {p1:.0%}   Requêtes parfaites@5 : {p5:.0%}   ({total} requêtes)")
    return 0 if p5 >= 0.6 else 1


if __name__ == "__main__":
    raise SystemExit(main())
