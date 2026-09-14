"""Vérificateur d'incertitude — la synthèse doit exprimer ses limites."""
from __future__ import annotations

import re

HEDGES = ("suspectée", "suspecté", "évoquer", "évoqué", "hypothèse", "possible",
          "probable", "compatible", "à confirmer", "suggestion", "orienter")


def expresses_uncertainty(text: str) -> bool:
    low = text.lower()
    return any(h in low for h in HEDGES)
