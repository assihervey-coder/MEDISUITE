"""Construction de citations à partir d'un EvidencePack."""
from __future__ import annotations

from tropirag.domain.evidence.entities import Citation, EvidencePack


def build_citations(pack: EvidencePack, top_n: int = 5) -> list[Citation]:
    cits: list[Citation] = []
    for i, u in enumerate(pack.top(top_n), start=1):
        quote = u.text.strip()
        if len(quote) > 220:
            quote = quote[:217].rstrip() + "…"
        cits.append(Citation(marker=f"[{i}]", unit_id=u.unit_id, quote=quote, full=u.citation()))
    return cits


def citations_by_marker(marker: str, cits: list[Citation]) -> Citation | None:
    for c in cits:
        if c.marker == marker:
            return c
    return None
