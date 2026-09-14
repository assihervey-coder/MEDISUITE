"""Escalade — qui doit voir ce patient, à quel niveau, avec quel message."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.core.enums import EscalationLevel, Urgency
from tropirag.clinical_engine.rules.rule_executor import RuleExecutionResult
from tropirag.clinical_engine.safety.safety_engine import SafetyAssessment

_URG_TO_LEVEL = {
    Urgency.IMMEDIATE: EscalationLevel.EMERGENCY_TRANSFER,
    Urgency.EMERGENCY: EscalationLevel.EMERGENCY_TRANSFER,
    Urgency.PRIORITY: EscalationLevel.REFER_HOSPITAL,
    Urgency.ROUTINE: EscalationLevel.SENIOR_CLINICIAN,
}


@dataclass(slots=True)
class EscalationPlan:
    level: EscalationLevel = EscalationLevel.NONE
    messages: list[str] = field(default_factory=list)
    requires_public_health_notification: bool = False
    requires_isolation: bool = False

    def to_dict(self) -> dict:
        return {"level": self.level.value, "messages": self.messages,
                "notify": self.requires_public_health_notification,
                "isolation": self.requires_isolation}


def build_escalation_plan(rules: RuleExecutionResult, safety: SafetyAssessment) -> EscalationPlan:
    plan = EscalationPlan()
    levels = [e.level for e in rules.escalations]
    if safety.max_urgency is not Urgency.ROUTINE:
        levels.append(_URG_TO_LEVEL[safety.max_urgency])
    if safety.isolation_required:
        plan.level = EscalationLevel.ISOLATION
    elif EscalationLevel.EMERGENCY_TRANSFER in levels:
        plan.level = EscalationLevel.EMERGENCY_TRANSFER
    elif EscalationLevel.REFER_HOSPITAL in levels:
        plan.level = EscalationLevel.REFER_HOSPITAL
    elif EscalationLevel.SENIOR_CLINICIAN in levels:
        plan.level = EscalationLevel.SENIOR_CLINICIAN
    for e in rules.escalations:
        plan.messages.append(f"[{e.level.value}] {e.message}")
    plan.requires_public_health_notification = bool(rules.notifications)
    plan.requires_isolation = safety.isolation_required
    # dédoublonnage en conservant l'ordre
    plan.messages = list(dict.fromkeys(plan.messages))
    return plan
