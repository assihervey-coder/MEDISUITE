"""Dépôt de propositions — protocole + implémentation filesystem (V1)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .entities import Proposal
from .value_objects import ProposalId


class ProposalRepository(Protocol):
    def save(self, proposal: Proposal) -> None: ...
    def get(self, proposal_id: ProposalId) -> Proposal | None: ...
    def list(self) -> list[Proposal]: ...
    def next_id(self) -> ProposalId: ...


class InMemoryProposalRepository:
    """Dépôt mémoire (tests + usage embarqué)."""

    def __init__(self) -> None:
        self._items: dict[str, Proposal] = {}
        self._counter = 0

    def save(self, proposal: Proposal) -> None:
        self._items[proposal.id.value] = proposal

    def get(self, proposal_id: ProposalId) -> Proposal | None:
        return self._items.get(proposal_id.value)

    def list(self) -> list[Proposal]:
        return sorted(self._items.values(), key=lambda p: p.id.value)

    def next_id(self) -> ProposalId:
        self._counter += 1
        return ProposalId(f"PROP-{self._counter:04d}")


class FileProposalRepository(InMemoryProposalRepository):
    """Dépôt YAML/JSON sur disque — source de vérité governance/proposals/registry."""

    def __init__(self, store_path: Path) -> None:
        super().__init__()
        self._path = Path(store_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if self._path.exists():
            data = json.loads(self._path.read_text(encoding="utf-8")) \
                if self._path.suffix == ".json" else {}
            for raw in data.get("proposals", []):
                try:
                    p = Proposal.from_dict(raw)
                    self._items[p.id.value] = p
                except (ValueError, KeyError):
                    continue  # entrées du registre YAML non encore homogènes

    def save(self, proposal: Proposal) -> None:
        super().save(proposal)
        payload = {"proposals": [p.to_dict() for p in self.list()]}
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                              encoding="utf-8")
