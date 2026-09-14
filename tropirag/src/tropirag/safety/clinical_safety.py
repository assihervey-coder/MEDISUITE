"""Sécurité clinique — disclaimers, vérifications de surface des réponses.

Toute réponse terminale DOIRT porter un disclaimer et refléter les drapeaux
rouges détectés. Ce module fournit les vérifications déterministes de
conformité d'une réponse clinique (indépendantes des guards IA).
"""
from __future__ import annotations

import re

from tropirag.core.constants import CLINICAL_DISCLAIMER_EN, CLINICAL_DISCLAIMER_FR

_URGENCY_KEYWORDS = {
    "immediate": ("immédiat", "urgence vitale", "sans délai", "référence immédiate"),
    "urgent": ("urgent", "dans l'heure", "rapidement"),
    "prompt": ("dans les 24", "prochainement", "à voir"),
}


def disclaimer(language: str = "fr") -> str:
    return CLINICAL_DISCLAIMER_FR if language == "fr" else CLINICAL_DISCLAIMER_EN


def verify_disclaimer(text: str, language: str = "fr") -> bool:
    """La réponse contient le disclaimer institutionnel (ou son noyau)."""
    target = disclaimer(language)
    nucleus = re.sub(r"\s+", " ", target[:60]).strip().lower()
    return nucleus[:30] in re.sub(r"\s+", " ", (text or "")).lower()


def urgency_conveyed(text: str, expected_urgency: str) -> bool:
    """Le niveau d'urgence attendu est-il perceptible dans le texte ?

    Vérification lexicale : pour un cas « immediate », la réponse doit porter
    au moins un marqueur d'immédiateté — sinon l'escalade risque d'être noyée.
    """
    expected = expected_urgency.lower()
    if expected not in _URGENCY_KEYWORDS:
        return True  # niveau inconnu → pas de contrôle
    low = (text or "").lower()
    return any(k in low for k in _URGENCY_KEYWORDS[expected])


def red_flag_acknowledged(text: str, red_flags: list[str]) -> dict:
    """Chaque drapeau rouge détecté doit être nommé dans la réponse."""
    low = (text or "").lower()
    missing = [f for f in red_flags
               if f and str(f).lower() not in low]
    return {"total": len(red_flags), "acknowledged": len(red_flags) - len(missing),
            "missing": missing,
            "passed": not missing}


def clinical_safety_report(text: str, urgency: str = "prompt",
                            red_flags: list[str] | None = None,
                            language: str = "fr") -> dict:
    """Rapport de sécurité clinique de surface d'une réponse terminale."""
    return {
        "disclaimer": verify_disclaimer(text, language),
        "urgency_conveyed": urgency_conveyed(text, urgency),
        "red_flags": red_flag_acknowledged(text, red_flags or []),
    }
