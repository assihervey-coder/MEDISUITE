"""Expansion de requête — synonymes cliniques FR/EN."""
from __future__ import annotations

EXPANSIONS = {
    "palu": "paludisme malaria",
    "malaria": "paludisme",
    "fièvre": "fièvre fever pyrexie",
    "typho": "typhoïde enteric fever salmonella",
    "ictère": "jaunisse ictere",
    "moustique": "anophèle aedes vecteur",
}


def expand(query: str) -> str:
    low = query.lower()
    extra = [syn for key, syn in EXPANSIONS.items() if key in low]
    return query + (" " + " ".join(extra) if extra else "")
