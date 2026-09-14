"""Adapter DeepSeek-R1 — audit logique : validation stricte des plages.

Le R1-Distill est un AUDITEUR, jamais un décideur : sa sortie ne contient
aucune action clinique, uniquement des verdicts de cohérence. Les plages
sont validées et bornées — un coverage hors [0,1] est un signal de sortie
corrompue → parse_ok=False.
"""
from __future__ import annotations

from typing import Any


def parse_audit(structured: Any) -> dict:
    if not isinstance(structured, dict):
        return {"consistent": None, "contradictions": [], "uncovered_findings": [],
                "unsupported_claims": [], "coverage": None, "parse_ok": False}
    raw_coverage = structured.get("coverage")
    coverage: float | None = None
    if isinstance(raw_coverage, (int, float)):
        c = float(raw_coverage)
        if 0.0 <= c <= 1.0:
            coverage = round(c, 4)
        else:
            # plage invalide → sortie corrompue, audit rejeté
            return {"consistent": None, "contradictions": [], "uncovered_findings": [],
                    "unsupported_claims": [], "coverage": None, "parse_ok": False}
    claims = [str(x) for x in structured.get("unsupported_claims", [])]
    return {
        "consistent": bool(structured.get("consistent", False)),
        "contradictions": sorted(str(x) for x in structured.get("contradictions", [])),
        "uncovered_findings": [str(x) for x in structured.get("uncovered_findings", [])],
        "unsupported_claims": claims,
        "coverage": coverage,
        "parse_ok": True,
    }
