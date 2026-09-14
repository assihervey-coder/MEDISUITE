"""Exécution des règles sur un cas → actions concrètes typées."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.core.enums import EscalationLevel, RuleActionType, Severity, Urgency
from tropirag.clinical_engine.rules.rule_engine import EvalContext, RuleEngine
from tropirag.domain.clinical_case.entities import ClinicalCase


@dataclass(slots=True)
class SuspicionEntry:
    disease: str
    weight: float
    rule_id: str
    note: str = ""
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RedFlagEntry:
    code: str
    severity: Severity
    urgency: Urgency
    message: str
    rule_id: str
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EscalationEntry:
    level: EscalationLevel
    message: str
    rule_id: str
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RequiredTestEntry:
    test_code: str
    reason: str
    rule_id: str


@dataclass(slots=True)
class DrugConstraintEntry:
    drug: str
    forbidden: bool
    reason: str
    rule_id: str


@dataclass(slots=True)
class RuleExecutionResult:
    suspicions: list[SuspicionEntry] = field(default_factory=list)
    red_flags: list[RedFlagEntry] = field(default_factory=list)
    escalations: list[EscalationEntry] = field(default_factory=list)
    required_tests: list[RequiredTestEntry] = field(default_factory=list)
    drug_constraints: list[DrugConstraintEntry] = field(default_factory=list)
    notifications: list[dict] = field(default_factory=list)
    informations: list[dict] = field(default_factory=list)
    matched_rule_ids: list[str] = field(default_factory=list)


class RuleExecutor:
    """Traduit les règles matchées en actions structurées."""

    def __init__(self, engine: RuleEngine) -> None:
        self.engine = engine

    def run(self, case: ClinicalCase) -> RuleExecutionResult:
        res = RuleExecutionResult()
        for outcome in self.engine.matched(case):
            rule = outcome.rule
            res.matched_rule_ids.append(rule.id)
            t = rule.then or {}
            at = RuleActionType(rule.action)

            if at is RuleActionType.RAISE_SUSPICION:
                res.suspicions.append(SuspicionEntry(
                    disease=t.get("disease", rule.disease or "unknown"),
                    weight=float(t.get("weight", rule.weight)),
                    rule_id=rule.id,
                    note=str(t.get("note", rule.description)),
                    evidence=list(rule.evidence),
                ))
            elif at is RuleActionType.RED_FLAG:
                res.red_flags.append(RedFlagEntry(
                    code=str(t.get("code", rule.id)),
                    severity=Severity(t.get("severity", "severe")),
                    urgency=Urgency(t.get("urgency", "emergency")),
                    message=str(t.get("message", rule.description)),
                    rule_id=rule.id,
                    evidence=list(rule.evidence),
                ))
            elif at is RuleActionType.ESCALATE:
                res.escalations.append(EscalationEntry(
                    level=EscalationLevel(t.get("level", "refer_hospital")),
                    message=str(t.get("message", rule.description)),
                    rule_id=rule.id,
                    evidence=list(rule.evidence),
                ))
            elif at is RuleActionType.REQUIRE_TEST:
                for test in t.get("tests", [t.get("test")]):
                    if test:
                        res.required_tests.append(RequiredTestEntry(
                            test_code=str(test),
                            reason=str(t.get("reason", rule.description)),
                            rule_id=rule.id,
                        ))
            elif at is RuleActionType.CONTRAINDICATE_DRUG:
                res.drug_constraints.append(DrugConstraintEntry(
                    drug=str(t.get("drug", "")),
                    forbidden=True,
                    reason=str(t.get("reason", rule.description)),
                    rule_id=rule.id,
                ))
            elif at is RuleActionType.RECOMMEND_DRUG:
                res.drug_constraints.append(DrugConstraintEntry(
                    drug=str(t.get("drug", "")),
                    forbidden=False,
                    reason=str(t.get("reason", rule.description)),
                    rule_id=rule.id,
                ))
            elif at is RuleActionType.NOTIFY:
                res.notifications.append({
                    "authority": t.get("authority", "public_health"),
                    "reason": str(t.get("reason", rule.description)),
                    "rule_id": rule.id,
                })
            else:  # inform
                res.informations.append({
                    "message": str(t.get("message", rule.description)),
                    "topic": t.get("topic"),
                    "rule_id": rule.id,
                })
        return res
