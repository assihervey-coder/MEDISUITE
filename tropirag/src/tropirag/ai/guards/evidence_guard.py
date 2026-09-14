"""Garde de preuve — pas de preuve, pas de synthèse.

Toute affirmation clinique d'une sortie IA doit être citée par un identifiant
d'unité de preuve VALIDE — présent dans le pack fourni pour cette requête.
Les citations fantômes (inventées) sont comptées comme échec.
"""
from __future__ import annotations

import re

from tropirag.ai.guards.input_guard import GuardResult, _fail, _pass
from tropirag.core.enums import RefusalReason
from tropirag.domain.evidence.entities import EvidencePack

_CITATION_RE = re.compile(r"\[([^\[\]]+)\]")


def extract_citations(text: str) -> list[str]:
    """Identifiants cités [EU-xxx] dans l'ordre d'apparition."""
    return [c.strip() for c in _CITATION_RE.findall(text or "")]


class EvidenceGuard:
    """Vérifie que les affirmations cliniques s'appuient sur le pack de preuves."""

    def __init__(self, min_citations: int = 1) -> None:
        self.min_citations = min_citations

    def check(self, text: str, pack: EvidencePack) -> GuardResult:
        if not pack.units:
            return _fail(RefusalReason.INSUFFICIENT_EVIDENCE,
                         "Aucune preuve disponible — la synthèse IA est refusée "
                         "(règle : pas de preuve, pas de synthèse).")
        cited = extract_citations(text)
        valid_ids = {u.unit_id for u in pack.units}
        valid = [c for c in cited if c in valid_ids]
        ghosts = [c for c in cited if c not in valid_ids]
        if ghosts:
            return _fail(RefusalReason.INSUFFICIENT_EVIDENCE,
                         f"Sortie rejetée : citation(s) invalide(s) {ghosts} — "
                         "inventer une référence est une faute grave.",
                         [f"ghost={g}" for g in ghosts])
        if len(valid) < self.min_citations:
            return _fail(RefusalReason.INSUFFICIENT_EVIDENCE,
                         f"Sortie rejetée : {len(valid)} citation(s) valide(s), "
                         f"{self.min_citations} requise(s). Toute affirmation clinique "
                         "doit être citée.")
        return _pass(findings=[f"citations valides: {valid}"])

    # ------------------------------------------------------------------
    def coverage(self, text: str, pack: EvidencePack) -> float:
        """Part des unités du pack effectivement citées (métrique)."""
        if not pack.units:
            return 0.0
        cited = set(extract_citations(text))
        used = {u.unit_id for u in pack.units if u.unit_id in cited}
        return round(len(used) / len(pack.units), 4)
