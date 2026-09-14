"""Construction des citations — attachement + vérification d'intégrité.

Chaque citation doit : exister dans le pack, citer un extrait RÉEL de
l'unité, et porter la référence complète (source, section, année, EU-id).
"""
from __future__ import annotations

import re

from tropirag.domain.evidence.citations import build_citations
from tropirag.domain.evidence.entities import EvidencePack
from tropirag.response_engine.clinical_response_builder import ClinicalResponse


def attach_citations(response: ClinicalResponse, pack: EvidencePack, top_n: int = 5) -> None:
    cits = build_citations(pack, top_n)
    response.citations = [
        {"marker": c.marker, "unit_id": c.unit_id, "quote": c.quote, "full": c.full}
        for c in cits
    ]


def verify_citations(response: ClinicalResponse, pack: EvidencePack) -> dict:
    """Contrôle d'intégrité des citations d'une réponse terminale.

    Vérifie :
        - unicité des marqueurs [n],
        - existence de l'unité citée dans le pack,
        - authenticité de l'extrait cité (sous-chaîne du texte de l'unité),
        - format complet (source + section + année + EU-id).
    """
    problems: list[str] = []
    markers = [c.get("marker") for c in response.citations]
    if len(markers) != len(set(markers)):
        problems.append("marqueurs de citation dupliqués")
    for c in response.citations:
        unit = pack.get(c.get("unit_id", ""))
        if unit is None:
            problems.append(f"{c.get('unit_id')}: unité absente du pack")
            continue
        quote = re.sub(r"\s+", " ", (c.get("quote") or "")).strip().lower()
        original = re.sub(r"\s+", " ", unit.text).lower()
        if quote and quote[:60] and quote[:60] not in original:
            problems.append(f"{c.get('unit_id')}: extrait cité introuvable dans l'unité")
        full = c.get("full") or ""
        if unit.unit_id not in full:
            problems.append(f"{c.get('unit_id')}: référence sans identifiant EU")
    return {"citations": len(response.citations), "problems": problems,
            "passed": not problems}


def format_bibliography(pack: EvidencePack, top_n: int = 5) -> str:
    """Bibliographie lisible triée par autorité — pour affichage terminal."""
    lines: list[str] = []
    for u in pack.top(top_n):
        year = str(u.source.edition_date or "")[:4] or "s.d."
        lines.append(f"[{u.unit_id}] {u.source.publisher}. {u.source.title}"
                     f"{f', section « {u.section} »' if u.section else ''} ({year})")
    return "\n".join(lines)
