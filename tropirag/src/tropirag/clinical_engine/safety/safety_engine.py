"""Safety Engine — synthèse déterministe de tous les signes de gravité.

Cette couche a l'autorité FINALE : aucune sortie IA ne peut la contourner.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.core.enums import EscalationLevel, Severity, Urgency
from tropirag.clinical_engine.rules.rule_executor import RuleExecutionResult
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.clinical_case.value_objects import CaseVerdict


@dataclass(slots=True)
class SafetyAssessment:
    """Résultat consolidé du Safety Engine."""

    max_severity: Severity = Severity.NONE
    max_urgency: Urgency = Urgency.ROUTINE
    red_flag_codes: list[str] = field(default_factory=list)
    isolation_required: bool = False
    notify_public_health: bool = False
    verdict: CaseVerdict = field(default_factory=CaseVerdict)
    blocking_messages: list[str] = field(default_factory=list)
    all_messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "max_severity": self.max_severity.value,
            "max_urgency": self.max_urgency.value,
            "red_flag_codes": self.red_flag_codes,
            "isolation_required": self.isolation_required,
            "notify_public_health": self.notify_public_health,
            "blocking_messages": self.blocking_messages,
            "all_messages": self.all_messages,
        }


_SEV_RANK = {Severity.NONE: 0, Severity.MILD: 1, Severity.MODERATE: 2, Severity.SEVERE: 3, Severity.CRITICAL: 4}
_URG_RANK = {Urgency.ROUTINE: 0, Urgency.PRIORITY: 1, Urgency.EMERGENCY: 2, Urgency.IMMEDIATE: 3}


class SafetyEngine:
    """Consolide rule-execution + constantes → verdict de sécurité global."""

    def assess(self, case: ClinicalCase, rules: RuleExecutionResult) -> SafetyAssessment:
        a = SafetyAssessment()
        sev, urg = Severity.NONE, Urgency.ROUTINE

        for rf in rules.red_flags:
            sev = max(sev, rf.severity, key=lambda s: _SEV_RANK[s])
            urg = max(urg, rf.urgency, key=lambda u: _URG_RANK[u])
            a.red_flag_codes.append(rf.code)
            a.all_messages.append(f"[{rf.severity.value.upper()}] {rf.message}")

        for esc in rules.escalations:
            a.all_messages.append(f"[{esc.level.value}] {esc.message}")
            if esc.level is EscalationLevel.ISOLATION:
                a.isolation_required = True
                urg = max(urg, Urgency.IMMEDIATE, key=lambda u: _URG_RANK[u])
                sev = max(sev, Severity.CRITICAL, key=lambda s: _SEV_RANK[s])
            elif esc.level is EscalationLevel.EMERGENCY_TRANSFER:
                urg = max(urg, Urgency.EMERGENCY, key=lambda u: _URG_RANK[u])
                sev = max(sev, Severity.SEVERE, key=lambda s: _SEV_RANK[s])
            elif esc.level is EscalationLevel.REFER_HOSPITAL:
                urg = max(urg, Urgency.PRIORITY, key=lambda u: _URG_RANK[u])

        if rules.notifications:
            a.notify_public_health = True

        # — constantes brutes (double filet, indépendant des règles) ————————
        if case.vitals.is_hypotension():
            urg = max(urg, Urgency.IMMEDIATE, key=lambda u: _URG_RANK[u])
            sev = max(sev, Severity.CRITICAL, key=lambda s: _SEV_RANK[s])
        if case.vitals.is_hypoxia() or case.vitals.is_unresponsive():
            urg = max(urg, Urgency.IMMEDIATE, key=lambda u: _URG_RANK[u])
            sev = max(sev, Severity.CRITICAL, key=lambda s: _SEV_RANK[s])

        a.max_severity = sev
        a.max_urgency = urg

        # messages bloquants = ceux qui conditionnent la réponse
        if sev in (Severity.SEVERE, Severity.CRITICAL):
            a.blocking_messages = list(dict.fromkeys(a.all_messages))

        # verdict
        must_not_miss = any(
            rf.code.startswith(("vhf", "lassa", "yf_toxic", "cerebral_malaria", "severe_anemia",
                                "dengue_shock", "dengue_warning_bleeding", "purpura", "hyperpyrexia"))
            for rf in rules.red_flags
        )
        a.verdict = CaseVerdict(
            urgency=urg,
            severity=sev,
            requires_isolation=a.isolation_required,
            must_not_miss_active=must_not_miss,
            refuse_synthesis=False,  # la synthèse est refusée plus haut si preuve absente
        )
        return a
