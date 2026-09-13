"""État partagé de l'API — dépôts en mémoire + chaîne d'audit filesystem."""
from __future__ import annotations

from pathlib import Path

from ..._bridge import register

register()
import importlib  # noqa: E402

_drepo = importlib.import_module("ecp.domain.proposal.repository")
_audit = importlib.import_module("ecp.adapters.repository.audit")

ROOT = Path(__file__).resolve().parents[4]


class State:
    def __init__(self) -> None:
        self.proposals = _drepo.InMemoryProposalRepository()
        self.assessments: dict[str, dict] = {}
        self.changes: dict[str, dict] = {}
        self.validations: dict[str, dict] = {}
        self.rollouts: dict[str, dict] = {}
        self.rollbacks: dict[str, dict] = {}
        self.audit = _audit.AuditChain(ROOT / "audit" / "evolution" / "api-events.jsonl")

    # helpers
    def get_proposal(self, pid: str) -> dict:
        p = self.proposals.get(_drepo.ProposalId(pid))
        if p is None:
            return {}
        return p.to_dict()


STATE = State()
