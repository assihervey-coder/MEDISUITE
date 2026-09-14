"""Classificateur d'intention — détection déterministe FR/EN.

Intentions V1 :
    clinical_analysis — analyse d'un cas (défaut),
    drug_check        — sécurité médicamenteuse,
    evidence_search   — recherche documentaire,
    info              — information générale,
    unsafe            — demande hors périmètre (reroutée vers refus).
"""
from __future__ import annotations

import re

from tropirag.query_engine.query_analyzer import QueryAnalysis, analyze_query  # noqa: F401

_INTENTS: list[tuple[str, str, list[str]]] = [
    ("unsafe", r"\b(?:pos[ée]s? un diagnostic|confirme que|dose exacte|"
     r"prescri[st] sans|remplace le m[ée]decin)\b"),
    ("drug_check", r"\b(?:m[ée]dicament|traitement|posologie|contre-indication|"
     r"interact|AINS|antibiotique|antipaludique|s[ûu]r pendant|peut[- ]on donner)\b"),
    ("evidence_search", r"\b(?:preuve|r[ée]f[ée]rence|source|recommandation|"
     r"directive|guideline|protocole|quelle [ée]tude|OMS dit)\b"),
    ("info", r"\b(?:qu'est-ce|c'est quoi|d[ée]finition|comment se transmet|"
     r"incubation|pr[ée]vention|vaccin)\b"),
]


def classify_intent(query: str) -> str:
    """Intention dominante — le premier motif gagnant, défaut clinical_analysis."""
    low = (query or "").lower()
    for intent, pattern in _INTENTS:
        if re.search(pattern, low):
            return intent
    if not low.strip():
        return "unknown"
    return "clinical_analysis"


def classify(query: str) -> dict:
    """Classification détaillée — intention + signaux détectés."""
    low = (query or "").lower()
    intent = classify_intent(query)
    signals = [name for name, pat in _INTENTS if re.search(pat, low)]
    return {"intent": intent, "signals": signals,
            "query_length": len(low.strip())}
