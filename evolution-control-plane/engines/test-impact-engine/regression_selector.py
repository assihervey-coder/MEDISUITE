"""Sélecteur de régression — règle P4+ = régression complète."""
from __future__ import annotations


def needs_full_regression(change_class: str) -> bool:
    """P4 (architecture) et au-dessus → régression complète obligatoire."""
    return int(change_class[1:]) >= 4
