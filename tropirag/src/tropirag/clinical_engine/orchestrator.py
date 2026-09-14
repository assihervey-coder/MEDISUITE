"""Clinical Orchestrator — chef d'orchestre déterministe du pipeline clinique.

Ordre sacré (jamais modifié) :
    CAS → RULES → SAFETY → TEMPORAL → DIFFERENTIEL
    → (puis, hors de ce module) QUERY → EVIDENCE → RAISONNEMENT IA → SAFETY GATE
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.clinical_engine.prioritization.differential_engine import (
    DifferentialEngine,
    DifferentialEntry,
    UncertaintyAssessor,
)
from tropirag.clinical_engine.rules.rule_executor import RuleExecutor, RuleExecutionResult
from tropirag.clinical_engine.rules.rule_loader import load_rule_engine
from tropirag.clinical_engine.safety.escalation_engine import EscalationPlan, build_escalation_plan
from tropirag.clinical_engine.safety.safety_engine import SafetyAssessment, SafetyEngine
from tropirag.clinical_engine.temporal.incubation_engine import IncubationEngine, TemporalReasoner
from tropirag.domain.clinical_case.builders import build_case
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.clinical_case.validators import validate_case


@dataclass(slots=True)
class ClinicalAnalysis:
    """Résultat complet de la phase déterministe."""

    case: ClinicalCase
    rules: RuleExecutionResult
    safety: SafetyAssessment
    escalation: EscalationPlan
    differentials: list[DifferentialEntry] = field(default_factory=list)
    uncertainty: dict = field(default_factory=dict)
    timeline_notes: list[str] = field(default_factory=list)
    validation_issues: list[str] = field(default_factory=list)
    matched_rule_ids: list[str] = field(default_factory=list)
    rules_fingerprint: str = ""


class ClinicalOrchestrator:
    """Exécute la chaîne déterministe complète sur un cas."""

    def __init__(self, rule_engine=None) -> None:
        self._engine = rule_engine or load_rule_engine()
        self._executor = RuleExecutor(self._engine)
        self._safety = SafetyEngine()
        self._differential = DifferentialEngine()
        self._uncertainty = UncertaintyAssessor()
        self._temporal = TemporalReasoner()

    def analyze(self, case: ClinicalCase) -> ClinicalAnalysis:
        rules_result = self._executor.run(case)
        safety = self._safety.assess(case, rules_result)
        escalation = build_escalation_plan(rules_result, safety)
        differentials = self._differential.build(case, rules_result)
        uncertainty = self._uncertainty.assess(differentials, case)
        timeline_notes = self._temporal.narrate(case)
        issues = validate_case(case)
        return ClinicalAnalysis(
            case=case,
            rules=rules_result,
            safety=safety,
            escalation=escalation,
            differentials=differentials,
            uncertainty=uncertainty,
            timeline_notes=timeline_notes,
            validation_issues=issues,
            matched_rule_ids=rules_result.matched_rule_ids,
            rules_fingerprint=self._engine.fingerprint(),
        )

    def analyze_payload(self, payload: dict) -> ClinicalAnalysis:
        return self.analyze(build_case(payload))
