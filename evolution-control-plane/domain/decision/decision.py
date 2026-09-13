"""Decision — moteur de quorum piloté par config/approval-matrix.yaml."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .entities import Approval, Decision

CONFIG = Path(__file__).resolve().parents[3] / "config" / "approval-matrix.yaml"

FALLBACK_MATRIX: dict[str, list[str]] = {
    "P1": [], "P2": [], "P3": ["maintainer"], "P4": ["maintainer", "security_officer"],
    "P5": ["maintainer", "data_protection"], "P6": ["maintainer", "clinical_lead"],
    "P7": ["clinical_lead", "safety_officer"],
    "P8": ["clinical_lead", "safety_officer", "security_officer"],
    "P9": ["regulatory_affairs", "clinical_lead", "safety_officer"],
}


def required_roles(change_class: str) -> list[str]:
    if CONFIG.exists():
        cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
        matrix = cfg.get("matrix") or FALLBACK_MATRIX
    else:
        matrix = FALLBACK_MATRIX
    return list(matrix.get(change_class, []))


class QuorumNotMet(Exception):
    pass


def evaluate_quorum(proposal_id: str, change_class: str,
                    approvals: list[Approval], author: str = "") -> Decision:
    """Approuve si TOUS les rôles requis ont approuvé, sans auto-approbation."""
    needed = required_roles(change_class)
    roles_ok = {a.role for a in approvals}
    missing = [r for r in needed if r not in roles_ok]
    self_approval = [a.role for a in approvals if a.actor == author and author]
    if self_approval:
        raise QuorumNotMet("séparation des devoirs : l'auteur ne peut s'approuver")
    if missing:
        raise QuorumNotMet(f"rôles manquants : {missing} (classe {change_class})")
    return Decision(proposal_id=proposal_id, outcome="APPROVED",
                    approvals=list(approvals))


def decision_to_dict(d: Decision) -> dict[str, Any]:
    return d.to_dict()
