"""Benchmark retrieval — harness complet du moteur de preuves.

Jeu de requêtes cliniques de référence avec unités pertinentes attendues
(validation par consensus du corpus) ; exécute le pipeline hybride complet
(BM25 + vecteurs + RRF + reranking + validation temporelle) et produit :
    - Recall@5 / Recall@10,
    - Precision@5,
    - MRR,
    - nDCG@10 (pertinence graduée par rang d'autorité de la source).

Usage :
    python -m evaluation.retrieval.benchmark          # exécution + rapport
    from evaluation.retrieval.benchmark import run    # API
"""
from __future__ import annotations

from evaluation.common import (
    MetricResult,
    SuiteReport,
    markdown_summary,
    write_report,
)
from evaluation.retrieval.ndcg import mean_ndcg
from evaluation.retrieval.precision import map_score, precision_at_k
from evaluation.retrieval.recall import mean_recall_at_k, mrr

# (requête terrain, {unit_id: gain}) — gain gradué : 2 = attendu direct,
# 1 = pertinent adjacent
BENCH: list[tuple[str, dict[str, float]]] = [
    ("fièvre voyage zone paludéenne suspicion",
     {"eu-who-mal-001": 2, "eu-ci-mal-009": 2}),
    ("paludisme sévère artésunate IV critères",
     {"eu-who-mals-005": 2, "eu-who-mals-006": 2, "eu-who-mal-001": 1}),
    ("paludisme grossesse artésunate quinine",
     {"eu-who-mip-001": 2, "eu-who-mip-002": 2}),
    ("dengue signes d'alarme AINS interdits",
     {"eu-who-den-002": 2, "eu-who-den-003": 2}),
    ("dengue enfant remplissage choc critique",
     {"eu-who-den-peds-001": 2, "eu-who-den-peds-002": 2}),
    ("typhoïde hémoculture diagnostic",
     {"eu-who-typ-001": 2, "eu-who-typ-002": 2}),
    ("typhoïde XDR azithromycine résistance",
     {"eu-cdc-typ-xdr-001": 2, "eu-who-typ-xdr-002": 2}),
    ("fièvre jaune ictère vaccination",
     {"eu-who-yf-001": 2, "eu-who-yf-002": 2}),
    ("ebola isolement 21 jours épidémie",
     {"eu-who-vhf-001": 2, "eu-who-vhf-002": 2}),
    ("méningite ceftriaxone urgence",
     {"eu-who-men-001": 2, "eu-who-men-002": 1}),
    ("purpura fulminans enfant",
     {"eu-who-men-002": 2, "eu-who-men-003": 2}),
    ("leptospirose eaux stagnantes ictère Weil",
     {"eu-who-lepto-001": 2, "eu-who-lepto-002": 2}),
    ("chikungunya arthralgies éruption",
     {"eu-who-chik-001": 2}),
    ("zika grossesse microcéphalie",
     {"eu-who-zik-001": 2}),
    ("TDR paludisme négatif interprétation",
     {"eu-who-mal-002": 2}),
    ("thrombopénie NS1 diagnostic dengue",
     {"eu-who-den-004": 2}),
    ("paludisme insuffisance rénale dialyse",
     {"eu-who-mal-renal-001": 2, "eu-who-mal-renal-002": 2}),
    ("drépanocytose fièvre pneumocoque urgence",
     {"eu-who-scd-001": 2, "eu-who-scd-002": 1}),
]

# seuils calibrés sur la base V1 (47 unités) — rappelés à chaque évolution du
# corpus ; precision plafonnée : |hits| / min(k, |pertinents|) car la plupart
# des requêtes n'ont que 1-3 unités pertinentes.
THRESHOLDS = {"recall@5": 0.80, "recall@10": 0.85, "precision@5_capped": 0.75,
              "mrr": 0.70, "ndcg@10": 0.75, "map": 0.60}


def run(engine=None) -> SuiteReport:
    """Exécute le benchmark complet du retrieval."""
    if engine is None:
        from tropirag.evidence_engine.evidence_engine import EvidenceEngine
        engine = EvidenceEngine()
        engine.load()
    report = SuiteReport(suite="retrieval")
    rankings: list[list[str]] = []
    relevants: list[set[str]] = []
    graded: list[dict[str, float]] = []

    for query, rel in BENCH:
        pack = engine.retrieve_evidence(query, top_k=10)
        ranked = [u.unit_id for u in pack.units]
        rankings.append(ranked)
        relevants.append(set(rel))
        graded.append(rel)
        report.cases.append({"query": query, "top10": ranked,
                             "expected": list(rel)})

    report.add(MetricResult("recall@5", mean_recall_at_k(rankings, relevants, 5),
                             THRESHOLDS["recall@5"]))
    report.add(MetricResult("recall@10", mean_recall_at_k(rankings, relevants, 10),
                             THRESHOLDS["recall@10"]))
    capped = []
    for r, rel in zip(rankings, relevants):
        hits = sum(1 for uid in r[:5] if uid in rel)
        capped.append(min(1.0, hits / min(5, len(rel))))
    p5c = sum(capped) / len(capped)
    report.add(MetricResult("precision@5_capped", p5c, THRESHOLDS["precision@5_capped"],
                            {"note": "hits/min(5, |pertinents|)"}))
    report.add(MetricResult("mrr", mrr(rankings, relevants), THRESHOLDS["mrr"]))
    report.add(MetricResult("ndcg@10", mean_ndcg(rankings, graded, 10),
                             THRESHOLDS["ndcg@10"]))
    report.add(MetricResult("map", map_score(rankings, relevants), THRESHOLDS["map"]))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    r = run()
    print(markdown_summary(r))
