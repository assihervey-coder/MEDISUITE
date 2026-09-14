"""Priorisation des preuves par maladie suspectée."""
from __future__ import annotations

from tropirag.domain.evidence.entities import EvidencePack


def prioritize_for_differentials(pack: EvidencePack, diseases: list[str], top_per_disease: int = 3) -> list[str]:
    """Renvoie les unit_ids les plus pertinentes par maladie (pré-fetch pour la synthèse)."""
    selected: list[str] = []
    for d in diseases:
        scored = sorted(
            (u for u in pack.units if d in u.diseases or d in u.topics),
            key=lambda u: pack.scores.get(u.unit_id, 0.0),
            reverse=True,
        )
        selected.extend(u.unit_id for u in scored[:top_per_disease])
    return list(dict.fromkeys(selected))
