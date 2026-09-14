"""Détection de contradictions règle ↔ synthèse."""
from __future__ import annotations

from tropirag.clinical_engine.rules.rule_executor import RuleExecutionResult


def check_drug_contradictions(text: str, rules: RuleExecutionResult) -> list[str]:
    """Une synthèse qui recommande un médicament interdit = contradiction."""
    issues: list[str] = []
    low = text.lower()
    for dc in rules.drug_constraints:
        if not dc.forbidden:
            continue
        if dc.drug.replace("_", " ") in low or dc.drug.replace("_", "-") in low:
            import re

            if re.search(rf"(administrer|donner|prescrire|utiliser|recommand)[^.]{{0,50}}"
                         rf"{dc.drug.replace('_', r'[ -]')}", low):
                issues.append(f"la synthèse recommande {dc.drug} pourtant interdit ({dc.reason})")
    return issues
