"""TropiRAG — évaluation scientifique du système.

Suites : retrieval (recall/precision/nDCG), grounding (couverture de preuve,
exactitude des citations, affirmations non soutenues), clinical (exactitude
des cas, qualité du différentiel, temporel, escalades), ai (modèles, routage,
latence, mémoire, taux d'échec), safety (invariants, refus, hallucination,
sorties dangereuses).

Chaque suite produit un rapport JSON + Markdown dans evaluation/reports/.
"""
from evaluation.common import (  # noqa: F401
    MetricResult,
    SuiteReport,
    load_dataset,
    load_json,
    write_report,
)
