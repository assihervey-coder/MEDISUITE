"""Precision@k et MAP — bruit du retrieval."""
from __future__ import annotations


def precision_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    """Part des unités du top-k qui sont pertinentes."""
    if k <= 0:
        return 0.0
    topk = ranked_ids[:k]
    if not topk:
        return 0.0
    return sum(1 for uid in topk if uid in relevant) / len(topk)


def average_precision(ranked_ids: list[str], relevant: set[str]) -> float:
    """AP — aire sous la courbe précision/rappel d'une requête."""
    if not relevant or not ranked_ids:
        return 0.0
    hits = 0
    total = 0.0
    for i, uid in enumerate(ranked_ids, start=1):
        if uid in relevant:
            hits += 1
            total += hits / i
    return total / len(relevant)


def map_score(rankings: list[list[str]], relevants: list[set[str]]) -> float:
    """Mean Average Precision sur un jeu de requêtes."""
    if not rankings:
        return 0.0
    return sum(average_precision(r, rel) for r, rel in zip(rankings, relevants)) / len(rankings)
