"""Garde clinique de surface — langage prudent et conformité de forme.

Non bloquant par défaut (avertissement) : vérifie la présence de modalisation
prudente (suspecté/évoquer/hypothèse…), du disclaimer, et l'absence de
promesses thérapeutiques. La tolérance zéro relève du Safety Gate global,
pas de cette passe de finition.
"""
from __future__ import annotations

import re

from tropirag.ai.guards.input_guard import GuardResult, _pass

# modalisation prudente attendue dans toute synthèse clinique
HEDGE_REQUIRED: list[str] = [
    r"\bpeut[- ]êtres?\b", r"\bsuspectée?\b", r"\b[ée]voquer\b",
    r"\bhypoth[èe]se\b", r"\bsugg[ée]r", r"\bprobable\b", r"\bcompatible\b",
    r"\b[ée]liminer\b", r"\bpossible\b", r"\battention\b",
    r"\bdoit être [ée]cartée?\b", r"\b[ée]carter\b", r"\bprudence\b",
]

# promesses thérapeutiques interdites
_NO_THERAPEUTIC_PROMISES = [
    r"\bgu[ée]rison (?:assurée|garantie)\b",
    r"\b sans (?:risque|danger)\b",
    r"\bsans effet secondaire\b",
    r"\brem[èe]de miracle\b",
    r"\btisane (?:qui )?gu[ée]rit\b",
]


class ClinicalGuard:
    """Vérifie la conformité clinique de surface (langage prudent, disclaimers)."""

    def __init__(self, require_disclaimer: bool = False) -> None:
        self.require_disclaimer = require_disclaimer

    def check(self, text: str, language: str = "fr") -> GuardResult:
        findings: list[str] = []
        low = (text or "").lower()
        if not any(re.search(p, low) for p in HEDGE_REQUIRED):
            findings.append("aucune modalisation prudente (suspecté/évoquer/hypothèse...)")
        for pat in _NO_THERAPEUTIC_PROMISES:
            if re.search(pat, low):
                findings.append(f"promesse thérapeutique interdite : {pat}")
        if self.require_disclaimer and "compagnon" not in low and "disclaimer" not in low:
            findings.append("disclaimer absent")
        if findings:
            # pas bloquant en soi : la reformulation est requise
            return GuardResult(
                passed=True, message="avertissement: " + "; ".join(findings),
                findings=findings)
        return _pass()
