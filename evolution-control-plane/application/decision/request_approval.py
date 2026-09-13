"""Cas d'usage — demande d'approbation (rôles requis par classe)."""
from __future__ import annotations

from ...domain.decision.decision import required_roles


def request_approval(proposal_id: str, change_class: str, author: str) -> dict:
    roles = required_roles(change_class)
    return {
        "proposal_id": proposal_id,
        "change_class": change_class,
        "required_roles": roles,
        "author": author,
        "note": "séparation des devoirs : l'auteur ne peut pas s'auto-approuver",
    }
