"""Checkpoints — snapshot restaurable d'une release."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .strategy import REQUIRED_CHECKPOINTS


@dataclass(slots=True)
class CheckpointSet:
    release_id: str
    present: set[str] = field(default_factory=set)
    artifacts: dict[str, str] = field(default_factory=dict)  # checkpoint → référence

    def add(self, checkpoint: str, artifact_ref: str) -> None:
        if checkpoint not in REQUIRED_CHECKPOINTS:
            raise ValueError(f"checkpoint inconnu : {checkpoint}")
        self.present.add(checkpoint)
        self.artifacts[checkpoint] = artifact_ref

    @property
    def ready(self) -> bool:
        return set(REQUIRED_CHECKPOINTS) <= self.present

    def to_dict(self) -> dict[str, Any]:
        return {"release_id": self.release_id, "ready": self.ready,
                "checkpoints": dict(self.artifacts)}
