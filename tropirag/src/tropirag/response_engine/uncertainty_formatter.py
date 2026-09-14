"""Formatage de l'incertitude — niveaux, motifs, impact sur la conduite.

L'incertitude n'est jamais cachée : elle est rendue EXPLICITE avec son
niveau (low/medium/high), ses motifs déterministes et son impact clinique
(« ne pas attendre la certitude pour agir » sur les maladies must-not-miss).
"""
from __future__ import annotations

import re

from tropirag.clinical_engine.orchestrator import ClinicalAnalysis
from tropirag.response_engine.clinical_response_builder import ClinicalResponse

_LEVELS = {
    "low": ("faible", "le tableau est suffisamment typé pour prioriser"),
    "medium": ("modérée", "des éléments manquent — compléter sans retarder les urgences"),
    "high": ("élevée", "présentation atypique — élargir le différentiel et réévaluer"),
}


def level_from_score(score: float) -> str:
    """Score d'incertitude [0,1] → niveau affichable."""
    if score >= 0.66:
        return "high"
    if score >= 0.33:
        return "medium"
    return "low"


def level_statement(level: str) -> str:
    label, guidance = _LEVELS.get(level, _LEVELS["medium"])
    return f"Incertitude {label} — {guidance}."


def attach_uncertainty(response: ClinicalResponse, analysis: ClinicalAnalysis) -> None:
    """Attache les notes d'incertitude formatées à la réponse."""
    u = analysis.uncertainty or {}
    notes = [u.get("statement", "")]
    notes += u.get("reasons", [])
    # niveau explicite si un score est disponible
    score = u.get("score") or u.get("level")
    if isinstance(score, (int, float)):
        level = level_from_score(float(score))
        notes.insert(0, level_statement(level))
    elif isinstance(score, str) and score in _LEVELS:
        notes.insert(0, level_statement(score))
    # maladies à ne jamais rater : l'incertitude ne doit jamais retarder
    if analysis.differentials:
        must_not_miss = [d for d in analysis.differentials
                         if getattr(getattr(d, "disease", None), "must_not_miss", False)]
        if must_not_miss:
            names = ", ".join(str(getattr(getattr(d, "disease", None), "label_fr", "?"))
                              for d in must_not_miss)
            notes.append(f"Ne pas attendre la certitude : {names} — "
                         "les critères d'urgence priment sur le diagnostic de certitude.")
    response.uncertainty_notes = [n for n in notes if n]


def uncertainty_summary(analysis: ClinicalAnalysis) -> dict:
    """Résumé structuré de l'incertitude (tableaux de bord)."""
    u = analysis.uncertainty or {}
    score = u.get("score")
    return {"statement": u.get("statement", ""),
            "reasons": list(u.get("reasons", [])),
            "level": level_from_score(float(score)) if isinstance(score, (int, float))
            else (score if score in _LEVELS else "medium")}
