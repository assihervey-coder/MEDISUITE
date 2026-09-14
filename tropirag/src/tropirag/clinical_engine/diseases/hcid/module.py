"""Spécialisation Infections à haut risque (MVH/HCID) — point d'entrée du module maladie."""
from __future__ import annotations

from typing import Callable

# Résumés cliniques structurés (critères OMS/MSF, seuils, déclarations)
from tropirag.clinical_engine.diseases.hcid import summaries as _summaries

# registre des fonctions exposées par le module — alimente les réponses
# déterministes et les prompts IA (contexte contrôlé, jamais de posologie)
_EXPOSED: dict[str, Callable] = {}


def register(name: str) -> Callable:
    """Décorateur : expose une fonction du module par nom."""
    def deco(fn):
        _EXPOSED[name] = fn
        return fn
    return deco


def available_summaries() -> list[str]:
    """Fonctions de résumé disponibles pour ce module."""
    return [n for n in dir(_summaries)
            if callable(getattr(_summaries, n)) and not n.startswith("_")]


def summary_function(name: str) -> Callable | None:
    return getattr(_summaries, name, None)


def module_info() -> dict:
    return {
        "disease_module": "hcid",
        "label_fr": "Infections à haut risque (MVH/HCID)",
        "summaries": available_summaries(),
    }
