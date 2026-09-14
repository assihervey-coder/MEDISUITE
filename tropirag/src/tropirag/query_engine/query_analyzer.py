"""Analyseur de requête — extrait intentions et concepts cliniques."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class QueryAnalysis:
    raw: str
    intent: str = "clinical_analysis"   # clinical_analysis | drug_check | info | unknown
    diseases_mentioned: list[str] = field(default_factory=list)
    symptoms_mentioned: list[str] = field(default_factory=list)
    drugs_mentioned: list[str] = field(default_factory=list)
    language: str = "fr"


_DISEASE_WORDS = {
    "paludisme": "malaria", "malaria": "malaria", "dengue": "dengue",
    "typho": "enteric_fever", "fièvre jaune": "yellow_fever",
    "ebola": "ebola", "lassa": "lassa", "marburg": "marburg",
    "chikungunya": "chikungunya", "zika": "zika",
    "méningite": "meningococcal", "leptospirose": "leptospirosis",
}
_DRUG_WORDS = ("ibuprofène", "ibuprofen", "aspirine", "paracétamol", "acetaminophen",
               "artésunate", "artemether", "coartem", "ceftriaxone", "azithromycine", "quinine")


def analyze_query(text: str) -> QueryAnalysis:
    low = text.lower()
    intent = "clinical_analysis"
    if re.search(r"(peux?[- ]je?|puis[- ]je|sûre?|interact|contre[- ]indic|associer)", low):
        intent = "drug_check"
    elif re.search(r"(c'est quoi|qu'est[- ]ce que|définition|explique)", low):
        intent = "info"
    diseases = sorted({code for w, code in _DISEASE_WORDS.items() if w in low})
    drugs = sorted({w for w in _DRUG_WORDS if w in low})
    return QueryAnalysis(raw=text, intent=intent, diseases_mentioned=diseases,
                         drugs_mentioned=drugs)
