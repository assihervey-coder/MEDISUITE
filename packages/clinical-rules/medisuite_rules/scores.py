"""Utilitaires génériques de scoring (somme pondérée, bandes de gravité)."""
from __future__ import annotations

from typing import Sequence


def sum_score(values: Sequence[bool | int | float],
              weights: Sequence[int | float] | None = None) -> int | float:
    """Somme pondérée : True compte 1 (ou son poids), False 0."""
    w = weights or [1] * len(values)
    return sum(v * weight for v, weight in zip(values, w) if v)


def grade(score: int | float, bands: Sequence[tuple[int | float, str]]) -> str:
    """Retourne l'étiquette du premier seuil atteint.

    bands = [(seuil_max_inclus, étiquette), ...] trié croissant ;
    la dernière étiquette couvre au-delà du dernier seuil.
    """
    for seuil, label in bands:
        if score <= seuil:
            return label
    return bands[-1][1]


def pct(value: float, low: float, high: float) -> float:
    """Position relative d'une valeur entre deux bornes (0..1, borné)."""
    if high <= low:
        raise ValueError("high doit être > low")
    return min(1.0, max(0.0, (value - low) / (high - low)))


def imc(poids_kg: float, taille_m: float) -> float:
    """Indice de masse corporelle (OMS)."""
    if taille_m <= 0:
        raise ValueError("taille invalide")
    return round(poids_kg / (taille_m ** 2), 1)


def categorie_oms(imc_value: float) -> str:
    """Classification OMS : maigreur <18.5, normal <25, surpoids <30, obésité."""
    return grade(imc_value, [(18.4, "maigreur"), (24.9, "normale"),
                             (29.9, "surpoids"), (999, "obésité")])
