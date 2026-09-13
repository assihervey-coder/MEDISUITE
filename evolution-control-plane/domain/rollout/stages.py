"""Stages de rollout — progression séquentielle avec gates."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Stage:
    name: str
    status: str = "PENDING"          # PENDING|ACTIVE|PASSED|FAILED|SKIPPED
    metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "status": self.status, "metrics": dict(self.metrics)}


class RolloutPlan:
    """Plan ordonné de stages ; on n'avance que si le stage courant PASSE."""

    def __init__(self, release_id: str, names: list[str]) -> None:
        self.release_id = release_id
        self.stages = [Stage(name=n) for n in names]
        if self.stages:
            self.stages[0].status = "ACTIVE"

    @property
    def current(self) -> Stage | None:
        return next((s for s in self.stages if s.status == "ACTIVE"), None)

    def advance(self) -> Stage | None:
        cur = self.current
        if cur is None:
            return None
        cur.status = "PASSED"
        idx = self.stages.index(cur) + 1
        if idx < len(self.stages):
            self.stages[idx].status = "ACTIVE"
            return self.stages[idx]
        return None

    def pause(self) -> None:
        cur = self.current
        if cur:
            cur.status = "PAUSED"

    def resume(self) -> None:
        for s in self.stages:
            if s.status == "PAUSED":
                s.status = "ACTIVE"
                return

    @property
    def finished(self) -> bool:
        return all(s.status in ("PASSED", "SKIPPED") for s in self.stages)

    def to_dict(self) -> dict[str, Any]:
        return {"release": self.release_id,
                "stages": [s.to_dict() for s in self.stages],
                "current_stage": self.current.name if self.current else None}
