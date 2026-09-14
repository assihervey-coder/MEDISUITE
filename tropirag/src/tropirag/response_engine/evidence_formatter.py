"""Formatage des preuves pour l'affichage."""
from __future__ import annotations

from tropirag.domain.evidence.entities import EvidencePack


def format_evidence_block(pack: EvidencePack, max_chars: int = 600) -> str:
    if pack.empty():
        return "Aucune preuve récupérée pour cette requête."
    lines = []
    for i, u in enumerate(pack.top(5), 1):
        text = u.text[:max_chars] + ("…" if len(u.text) > max_chars else "")
        lines.append(f"[{i}] {u.source.publisher} — {u.source.title}"
                     f"{' (' + str(u.source.edition_date)[:4] + ')' if u.source.edition_date else ''}\n"
                     f"    {text}\n    ↳ {u.unit_id}")
    return "\n\n".join(lines)
