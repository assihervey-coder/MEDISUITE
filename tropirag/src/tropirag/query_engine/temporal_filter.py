"""Filtre temporel — préférence aux éditions récentes, dépréciation douce.

Politique :
    - une édition de plus de PÉRIODE_DUREE années est pénalisée (score
      dégressif) mais JAMAIS exclue seule — la directive OMS de 2018 sur la
      typhoïde reste la référence si rien de plus récent n'existe,
    - l'ancienneté seule ne suffit jamais : l'exclusion relève du
      TemporalValidator (valid_until/superseded_by explicites).
"""
from __future__ import annotations

from datetime import date

MAX_EDITION_AGE_YEARS = 10          # au-delà : pénalité maximale
PENALTY_FLOOR = 0.3                 # jamais en dessous de 30 % du score


def edition_year(source) -> int | None:
    try:
        return int(str(source.edition_date)[:4])
    except (TypeError, ValueError):
        return None


def edition_age_years(source, ref: date | None = None) -> int | None:
    """Âge de l'édition en années complètes (None si inconnu)."""
    y = edition_year(source)
    if y is None:
        return None
    ref = ref or date.today()
    return max(0, ref.year - y)


def recency_factor(source, ref: date | None = None) -> float:
    """Facteur multiplicatif [PENALTY_FLOOR, 1] selon la fraîcheur."""
    age = edition_age_years(source, ref)
    if age is None:
        return 0.8  # date inconnue : légère méfiance, pas d'exclusion
    if age <= 3:
        return 1.0
    if age >= MAX_EDITION_AGE_YEARS:
        return PENALTY_FLOOR
    # décroissance linéaire de 1.0 (3 ans) à 0.3 (10 ans)
    frac = (age - 3) / (MAX_EDITION_AGE_YEARS - 3)
    return round(1.0 - frac * (1.0 - PENALTY_FLOOR), 4)


def sort_by_recency(units: list) -> list:
    """Tri par fraîcheur d'édition décroissante (stabilisé par unit_id)."""
    return sorted(units, key=lambda u: (-(edition_year(u.source) or 0), u.unit_id))
