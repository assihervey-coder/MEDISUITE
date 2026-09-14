"""Filtre de juridiction pour le retrieval.

Politique V1 : une unité est applicable si sa juridiction est
    - INT (universelle), ou
    - celle du déploiement (défaut CI), ou
    - celle d'un pays du corridor d'Afrique de l'Ouest partagé (interoper.
      régionale — les directives MSF/OMS Afrique se recoupent).
"""
from __future__ import annotations

# corridor régional deinteropérabilité — directives interchangeables
_WEST_AFRICA = {"CI", "SN", "GH", "ML", "BF", "BJ", "TG", "NE", "GN", "LR", "GM"}


def applicable_jurisdictions(user_jurisdiction: str) -> list[str]:
    """INT (universel) + juridiction utilisateur."""
    return ["INT", str(user_jurisdiction).upper()]


def jurisdiction_ok(unit_jurisdiction: str, user_jurisdiction: str = "CI",
                    regional: bool = True) -> bool:
    """Une unité est-elle applicable dans la juridiction du déploiement ?"""
    uj = str(unit_jurisdiction or "INT").upper()
    uj = "INT" if uj in ("", "WORLD", "GLOBAL") else uj
    user = str(user_jurisdiction or "CI").upper()
    if uj in ("INT", user):
        return True
    return regional and uj in _WEST_AFRICA and user in _WEST_AFRICA


def filter_by_jurisdiction(units: list, user_jurisdiction: str = "CI",
                            regional: bool = True) -> list:
    """Filtre une liste d'unités de preuve par applicabilité juridictionnelle."""
    return [u for u in units
            if jurisdiction_ok(getattr(u, "jurisdiction", "INT"),
                              user_jurisdiction, regional)]
