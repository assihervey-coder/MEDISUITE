"""Recall@k et MRR — couverture des unités pertinentes."""
from __future__ import annotations


def recall_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    """Part des unités pertinentes retrouvées dans le top-k."""
    if not relevant:
        return 1.0
    topk = set(ranked_ids[:k])
    return len(topk & relevant) / len(relevant)


def mean_recall_at_k(rankings: list[list[str]], relevants: list[set[str]],
                     k: int) -> float:
    """Recall@k moyen sur un jeu de requêtes."""
    if len(rankings) != len(relevants) or not rankings:
        return 0.0
    return sum(recall_at_k(r, rel, k) for r, rel in zip(rankings, relevants)) / len(rankings)


def reciprocal_rank(ranked_ids: list[str], relevant: set[str]) -> float:
    """1/rang de la première unité pertinente (0 si aucune)."""
    for i, uid in enumerate(ranked_ids, start=1):
        if uid in relevant:
            return 1.0 / i
    return 0.0


def mrr(rankings: list[list[str]], relevants: list[set[str]]) -> float:
    """Mean Reciprocal Rank sur un jeu de requêtes."""
    if not rankings:
        return 0.0
    return sum(reciprocal_rank(r, rel) for r, rel in zip(rankings, relevants)) / len(rankings)
