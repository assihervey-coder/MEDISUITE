"""Entité agrégat Proposal + événements du domaine."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .enums import ChangeClass, ImpactLevel, Outcome, Priority, ProposalState, ProposalType
from .events import (PROPOSAL_APPROVED, PROPOSAL_CLASSIFIED, PROPOSAL_REJECTED,
                     emit)
from .policies import GateMissing, TransitionDenied, assert_transition
from .value_objects import ImpactVector, ProposalId, now_iso  # noqa: F401


@dataclass(slots=True)
class Proposal:
    """Agrégat racine — une proposition versionnée et immuablement identifiée."""

    id: ProposalId
    version: int = 1
    title: str = ""
    status: ProposalState = ProposalState.DRAFT
    type: ProposalType = ProposalType.FEATURE
    priority: Priority = Priority.MEDIUM
    requested_by: str = "unknown"
    affected_domains: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    breaking_change: bool = False
    impacts: ImpactVector = field(default_factory=ImpactVector)
    migration_required: bool = False
    human_approval_required: bool = True
    rollback_required: bool = True
    change_class: ChangeClass | None = None
    provided_gates: set[str] = field(default_factory=set)
    history: list[dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------------- cycle
    def transition(self, target: ProposalState, actor: str = "system",
                   reason: str = "") -> None:
        assert_transition(self.status, target, self.change_class, self.provided_gates)
        evt = emit("PROPOSAL_TRANSITION", proposal_id=self.id.value,
                   previous_state=self.status.value, new_state=target.value,
                   actor=actor, reason=reason)
        self.history.append(evt)
        self.status = target

    def submit(self, actor: str = "system") -> None:
        if not self.title or len(self.title) < 5:
            raise ValueError("titre requis (≥ 5 caractères) avant soumission")
        self.transition(ProposalState.SUBMITTED, actor, "soumission")

    def classify(self, actor: str = "system",
                 override: ChangeClass | None = None) -> ChangeClass:
        """Classification = max(plancher type, plancher chemins, breaking)."""
        from .policies import classify_by_paths
        if override is not None:
            klass = max(override, classify_by_paths(self.changed_paths, self.type,
                                                    self.breaking_change),
                        key=lambda c: int(c.value[1:]))
        else:
            klass = classify_by_paths(self.changed_paths, self.type, self.breaking_change)
        self.change_class = klass
        self.transition(ProposalState.CLASSIFIED, actor,
                        f"classe {klass.value}")
        emit(PROPOSAL_CLASSIFIED, proposal_id=self.id.value, change_class=klass.value)
        return klass

    def decide(self, outcome: Outcome, actor: str = "committee", reason: str = "",
               conditions: list[str] | None = None) -> None:
        if self.status is not ProposalState.DECISION_PENDING:
            raise TransitionDenied("décision possible seulement depuis DECISION_PENDING")
        if outcome is Outcome.APPROVED and self.human_approval_required and not reason:
            raise ValueError("motif requis pour une approbation tracée")
        self.transition(ProposalState[outcome.value], actor, reason)
        emit(f"Proposal{'Approved' if outcome is Outcome.APPROVED else 'Rejected' if outcome is Outcome.REJECTED else 'Deferred'}",
             proposal_id=self.id.value, actor=actor, reason=reason,
             conditions=conditions or [])

    def attach_gate(self, gate: str) -> None:
        self.provided_gates.add(gate)

    # ------------------------------------------------------------- helpers
    def requires_full_regression(self) -> bool:
        return self.change_class is not None and int(self.change_class.value[1:]) >= 4

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id.value, "version": self.version, "title": self.title,
            "status": self.status.value, "type": self.type.value,
            "priority": self.priority.value, "requested_by": self.requested_by,
            "affected_domains": list(self.affected_domains),
            "changed_paths": list(self.changed_paths),
            "breaking_change": self.breaking_change,
            "impacts": {k: v.value for k, v in asdict(self.impacts).items()},
            "migration_required": self.migration_required,
            "human_approval_required": self.human_approval_required,
            "rollback_required": self.rollback_required,
            "change_class": self.change_class.value if self.change_class else None,
            "provided_gates": sorted(self.provided_gates),
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Proposal":
        impacts = ImpactVector(**{k: ImpactLevel(v) for k, v in
                                  (data.get("impacts") or {}).items()})
        return cls(
            id=ProposalId(data["id"]), version=data.get("version", 1),
            title=data.get("title", ""), status=ProposalState(data.get("status", "DRAFT")),
            type=ProposalType(data.get("type", "FEATURE")),
            priority=Priority(data.get("priority", "MEDIUM")),
            requested_by=data.get("requested_by", "unknown"),
            affected_domains=list(data.get("affected_domains", [])),
            changed_paths=list(data.get("changed_paths", [])),
            breaking_change=bool(data.get("breaking_change", False)),
            impacts=impacts,
            migration_required=bool(data.get("migration_required", False)),
            human_approval_required=bool(data.get("human_approval_required", True)),
            rollback_required=bool(data.get("rollback_required", True)),
            change_class=ChangeClass(data["change_class"]) if data.get("change_class") else None,
            provided_gates=set(data.get("provided_gates", [])),
            history=list(data.get("history", [])),
        )
