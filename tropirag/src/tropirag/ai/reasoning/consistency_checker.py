"""Vérification de cohérence déterministe."""
from __future__ import annotations

import re


def check_internal_consistency(text: str) -> list[str]:
    """Contradictions basiques détectables par patrons."""
    issues: list[str] = []
    low = text.lower()
    pairs = [
        (r"aucun (?:signe|symptôme)", r"symptômes? (?:présents|retrouvés)"),
        (r"tdr (?:négatif|negatif)", r"paludisme (?:confirmé|certain)"),
        (r"exclure la dengue", r"dengue (?:confirmée|certaine)"),
    ]
    for a, b in pairs:
        if re.search(a, low) and re.search(b, low):
            issues.append(f"contradiction possible : « {a} » vs « {b} »")
    return issues
