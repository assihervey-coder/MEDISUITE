"""Détection de contradictions entre unités de preuve."""
from __future__ import annotations

import re

from tropirag.domain.evidence.entities import EvidenceUnit
from tropirag.core.enums import SourceAuthority, AUTHORITY_RANK

OPPOSITES = [
    ("recommandé", "contre-indiqué"),
    ("première intention", "déconseillé"),
    ("formellement déconseillés", "traitement de référence"),
]


def detect_pairs(units: list[EvidenceUnit]) -> list[dict]:
    """Signale les paires d'unités qui se contredisent potentiellement."""
    findings: list[dict] = []
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            a, b = units[i], units[j]
            if set(a.diseases) & set(b.diseases):
                for pos, neg in OPPOSITES:
                    if (pos in a.text.lower() and neg in b.text.lower()) or \
                       (neg in a.text.lower() and pos in b.text.lower()):
                        findings.append({
                            "pair": [a.unit_id, b.unit_id],
                            "note": f"« {pos} » vs « {neg} »",
                            "resolution": "l'autorité de rang le plus bas cède "
                                          "(ou conflit documenté dans evidence_policy)",
                        })
    return findings
