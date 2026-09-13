"""État partagé de l'API — dépôts en mémoire + chaîne d'audit filesystem."""
from __future__ import annotations

import os
from pathlib import Path

from ..._bridge import register

register()
import importlib  # noqa: E402

_drepo = importlib.import_module("ecp.domain.proposal.repository")
_audit = importlib.import_module("ecp.adapters.repository.audit")

# Racine du dépôt gouverné (medisuite/) — PROP-0012 : parents[4] pointait un
# niveau trop haut, la chaîne d'audit WORM s'écrivait HORS du dépôt.
ROOT = Path(__file__).resolve().parents[3]

# Override d'isolation (tests) : ECP_AUDIT_PATH redirige la chaîne hors du
# dépôt pour ne jamais polluer les preuves de gouvernance réelles.
AUDIT_PATH = Path(os.environ.get("ECP_AUDIT_PATH")
                  or ROOT / "audit" / "evolution" / "api-events.jsonl")


class State:
    def __init__(self) -> None:
        self.proposals = _drepo.InMemoryProposalRepository()
        self.assessments: dict[str, dict] = {}
        self.changes: dict[str, dict] = {}
        self.validations: dict[str, dict] = {}
        self.rollouts: dict[str, dict] = {}
        self.rollbacks: dict[str, dict] = {}
        self.audit = _audit.AuditChain(AUDIT_PATH)

    # helpers
    def get_proposal(self, pid: str) -> dict:
        p = self.proposals.get(_drepo.ProposalId(pid))
        if p is None:
            return {}
        return p.to_dict()


STATE = State()
