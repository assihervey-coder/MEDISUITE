"""ChangeSet — conteneur immuable d'une implémentation approuvée."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from ..proposal.value_objects import ChangeSetId


@dataclass(slots=True)
class ChangeSet:
    """Créé APRÈS approbation ; figé par un checksum ; non ré-ouvrable."""

    id: ChangeSetId
    proposal: str
    baseline_version: str
    baseline_commit: str
    target_version: str
    modifications: list[str]                  # ADD | MODIFY | MIGRATE | REMOVE
    affected_components: list[str]
    migration_required: bool = False
    rollback_supported: bool = True
    units: list["ChangeUnit"] = field(default_factory=list)
    checksum: str = ""
    frozen: bool = False

    def add_unit(self, unit: "ChangeUnit") -> None:
        if self.frozen:
            raise RuntimeError(f"{self.id.value} est figé (imuable)")
        self.units.append(unit)

    def freeze(self) -> str:
        """Fige le change set et retourne son checksum SHA-256."""
        payload = json.dumps({
            "id": self.id.value, "proposal": self.proposal,
            "baseline_version": self.baseline_version,
            "baseline_commit": self.baseline_commit,
            "target_version": self.target_version,
            "modifications": self.modifications,
            "affected_components": self.affected_components,
            "units": [u.to_dict() for u in self.units],
        }, sort_keys=True, ensure_ascii=False)
        self.checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.frozen = True
        return self.checksum

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id.value, "proposal": self.proposal,
            "baseline": {"version": self.baseline_version,
                         "commit": self.baseline_commit},
            "target": {"version": self.target_version},
            "modifications": list(self.modifications),
            "affected_components": list(self.affected_components),
            "migration_required": self.migration_required,
            "rollback_supported": self.rollback_supported,
            "units": [u.to_dict() for u in self.units],
            "checksum": self.checksum, "immutable": self.frozen,
        }
