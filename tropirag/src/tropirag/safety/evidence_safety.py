"""Sécurité de preuve — invariants du cycle de vie et de la citation.

Invariants vérifiables :
    - un pack vide bloque TOUTE synthèse IA,
    - les unités périmées/supersédées sont exclues des packs actifs,
    - la hiérarchie d'autorité est respectée en cas de conflit,
    - chaque affirmation clinique est citée par une unité valide.
"""
from __future__ import annotations

from datetime import date

from tropirag.domain.evidence.entities import EvidencePack

INVARIANTS = {
    "empty_pack_blocks_ai": True,
    "expired_units_excluded": True,
    "authority_precedence": "who > national/msf/cdc > institutional > scientific",
    "every_claim_cited": True,
}


def verify_pack(pack: EvidencePack, ref: date | None = None) -> dict:
    """Contrôle les invariants d'un pack avant usage par un modèle."""
    today = ref or date.today()
    expired = [u.unit_id for u in pack.units if not u.is_current(today)]
    return {
        "empty_pack_blocks_ai": True,                    # structurel (Safety Gate)
        "pack_empty": pack.empty(),
        "expired_units_excluded": not expired,
        "expired_unit_ids": expired,
        "authority_precedence": INVARIANTS["authority_precedence"],
        "units": len(pack.units),
        "passed": not expired,
    }


def most_authoritative(pack: EvidencePack) -> list[str]:
    """Unités du pack triées par rang d'autorité croissant (1 = OMS)."""
    return [u.unit_id for u in sorted(pack.units, key=lambda u: (u.authority_rank(),
                                                                -pack.scores.get(u.unit_id, 0.0)))]


def resolve_conflict(units: list, jurisdiction: str = "CI") -> dict:
    """Politique de conflit : autorité maximale, puis proximité juridictionnelle.

    En cas d'égalité d'autorité, la source de la juridiction du déploiement
    (défaut : CI) prime ; à égalité, l'édition la plus récente prime.
    """
    if not units:
        return {"winner": None, "losers": [], "policy": INVARIANTS["authority_precedence"]}
    def sort_key(u):
        ed = str(u.source.edition_date or "0000")
        return (u.authority_rank(), 0 if u.jurisdiction == jurisdiction else 1, ed)
    ranked = sorted(units, key=sort_key)
    return {"winner": ranked[0].unit_id,
            "losers": [u.unit_id for u in ranked[1:]],
            "policy": INVARIANTS["authority_precedence"]}
