"""ChangeUnit — atome de modification au sein d'un change set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ChangeUnit:
    """Une unité vérifiable : ADD/MODIFY/MIGRATE/REMOVE sur un composant."""

    kind: str                    # ADD | MODIFY | MIGRATE | REMOVE
    component: str               # composant baseline (ex. patient-context)
    description: str
    paths: list[str] = field(default_factory=list)
    verify: str = ""             # commande de vérification (pytest, --check…)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "component": self.component,
                "description": self.description, "paths": list(self.paths),
                "verify": self.verify}
