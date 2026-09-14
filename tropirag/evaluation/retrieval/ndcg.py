"""nDCG — qualité ORDONNÉE du ranking (pertinence graduée)."""
from __future__ import annotations

import math


def dcg(gains: list[float]) -> float:
    """Discounted Cumulative Gain — gain logarithmiquement décroissant."""
    return sum(g / math.log2(i + 2) for i, g in enumerate(gains))


def ndcg(ranked_ids: list[str], graded_relevance: dict[str, float],
         k: int | None = None) -> float:
    """Normalized DCG — compare le ranking au classement idéal.

    graded_relevance : unit_id → gain (0 = non pertinent, >0 gradué).
    """
    ids = ranked_ids[: k] if k else ranked_ids
    if not ids:
        return 0.0
    gains = [float(graded_relevance.get(uid, 0.0)) for uid in ids]
    ideal = sorted(graded_relevance.values(), reverse=True)[: len(ids)]
    ideal = [g for g in ideal if g > 0]
    ideal += [0.0] * (len(ids) - len(ideal))
    d = dcg(gains)
    i = dcg(ideal)
    return d / i if i > 0 else (1.0 if not any(g > 0 for g in gains) else 0.0)


def mean_ndcg(rankings: list[list[str]], graded: list[dict[str, float]],
              k: int | None = None) -> float:
    """nDCG moyen sur un jeu de requêtes."""
    if not rankings:
        return 0.0
    return sum(ndcg(r, g, k) for r, g in zip(rankings, graded)) / len(rankings)
