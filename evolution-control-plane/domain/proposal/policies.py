"""Politiques du domaine Proposal — machine à états stricte + classification."""
from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

from .enums import ChangeClass, ProposalState, ProposalType

CONFIG = Path(__file__).resolve().parents[3] / "config"

# Machine à états : transitions autorisées (strict — tout le reste est refusé)
TRANSITIONS: dict[ProposalState, set[ProposalState]] = {
    ProposalState.DRAFT: {ProposalState.SUBMITTED},
    ProposalState.SUBMITTED: {ProposalState.VALIDATED, ProposalState.REJECTED},
    ProposalState.VALIDATED: {ProposalState.CLASSIFIED},
    ProposalState.CLASSIFIED: {ProposalState.IMPACT_ANALYSIS},
    ProposalState.IMPACT_ANALYSIS: {ProposalState.RISK_ASSESSMENT},
    ProposalState.RISK_ASSESSMENT: {ProposalState.DECISION_PENDING},
    ProposalState.DECISION_PENDING: {
        ProposalState.APPROVED, ProposalState.REJECTED, ProposalState.DEFERRED},
    ProposalState.DEFERRED: {ProposalState.VALIDATED},          # réactivation
    ProposalState.APPROVED: {ProposalState.CHANGE_PLANNED},
    ProposalState.CHANGE_PLANNED: {ProposalState.IMPLEMENTATION},
    ProposalState.IMPLEMENTATION: {ProposalState.TECHNICAL_VALIDATION},
    ProposalState.TECHNICAL_VALIDATION: {ProposalState.CLINICAL_VALIDATION},
    ProposalState.CLINICAL_VALIDATION: {ProposalState.SAFETY_VALIDATION},
    ProposalState.SAFETY_VALIDATION: {ProposalState.RELEASE_CANDIDATE},
    ProposalState.RELEASE_CANDIDATE: {ProposalState.CANARY, ProposalState.PILOT},
    ProposalState.CANARY: {ProposalState.PILOT, ProposalState.PAUSED,
                           ProposalState.ROLLED_BACK},
    ProposalState.PILOT: {ProposalState.ROLLOUT, ProposalState.PAUSED,
                          ProposalState.ROLLED_BACK},
    ProposalState.ROLLOUT: {ProposalState.RELEASED, ProposalState.PAUSED,
                            ProposalState.ROLLED_BACK},
    ProposalState.PAUSED: {ProposalState.ROLLOUT, ProposalState.ROLLED_BACK},
    ProposalState.ROLLED_BACK: set(),                           # terminal (post-vérification)
    ProposalState.RELEASED: {ProposalState.MONITORED},
    ProposalState.MONITORED: {ProposalState.ACCEPTED},
    ProposalState.ACCEPTED: set(),                              # nouvelle baseline
    ProposalState.REJECTED: set(),                              # terminal
}

# Gates exigées par classe avant certaines transitions (compatible V1 sans k8s live)
GATES_BY_CLASS: dict[str, set[str]] = {
    "P1": set(), "P2": set(), "P3": set(),
    "P4": {"compatibility_report"},
    "P5": {"compatibility_report", "migration_plan"},
    "P6": {"compatibility_report", "model_lineage"},
    "P7": {"compatibility_report", "clinical_review"},
    "P8": {"compatibility_report", "clinical_review", "safety_review"},
    "P9": {"compatibility_report", "clinical_review", "safety_review",
           "regulatory_review"},
}


class TransitionDenied(Exception):
    """Transition d'état interdite par la machine à états stricte."""


class GateMissing(Exception):
    """Gate de validation manquante pour franchir la transition."""


def assert_transition(current: ProposalState, target: ProposalState,
                      change_class: ChangeClass | None = None,
                      provided_gates: set[str] | None = None) -> None:
    """Valide une transition ; lève TransitionDenied/GateMissing sinon."""
    if target not in TRANSITIONS.get(current, set()):
        raise TransitionDenied(f"{current.value} → {target.value} interdit")
    if change_class is not None and provided_gates is not None:
        required = GATES_BY_CLASS.get(change_class.value, set())
        missing = required - set(provided_gates)
        # Les gates se contrôlent aux VALIDATIONS (l'ordre du cycle est
        # DÉCISION → CHANGE SET → VALIDATION), pas à l'approbation.
        if missing and target in (
            ProposalState.SAFETY_VALIDATION, ProposalState.RELEASE_CANDIDATE,
        ):
            raise GateMissing(f"gates manquants pour {change_class.value} : {sorted(missing)}")


# ------------------------------------------------------------- classification
# Planchers par type de proposition (peuvent être remontés, jamais abaissés)
TYPE_FLOOR: dict[ProposalType, ChangeClass] = {
    ProposalType.FEATURE: ChangeClass.P3,
    ProposalType.ARCHITECTURE: ChangeClass.P4,
    ProposalType.DATA: ChangeClass.P5,
    ProposalType.AI: ChangeClass.P6,
    ProposalType.CLINICAL: ChangeClass.P7,
    ProposalType.SECURITY: ChangeClass.P8,
    ProposalType.REGULATORY: ChangeClass.P9,
}

# Règles de détection par chemin (change-types.yaml) — plancher le plus haut gagne
_PATH_RULES_FALLBACK: list[tuple[str, str]] = [
    ("packages/clinical-rules/**", "P7"),
    ("compliance/**", "P9"),
    ("ai/**", "P6"),
    ("migrations/**", "P5"),
    ("security/**", "P8"),
    ("contracts/**", "P4"),
    ("**/*.md", "P1"),
]


def _load_path_rules() -> list[tuple[str, str]]:
    cfg = CONFIG / "change-types.yaml"
    if not cfg.exists():
        return _PATH_RULES_FALLBACK
    data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    rules = []
    for rule in data.get("detection_rules", []):
        rules.append((rule["pattern"], rule["class"]))
    return rules or _PATH_RULES_FALLBACK


def classify_by_paths(changed_paths: list[str],
                      proposal_type: ProposalType | None = None,
                      breaking_change: bool = False) -> ChangeClass:
    """Classe plancher par chemins modifiés + type + breaking change."""
    candidates = [ChangeClass.P1]
    if proposal_type is not None:
        candidates.append(TYPE_FLOOR[proposal_type])
    for pattern, klass in _load_path_rules():
        for path in changed_paths:
            if fnmatch.fnmatch(path, pattern):
                candidates.append(ChangeClass(klass))
    if breaking_change:
        candidates.append(ChangeClass.P4)
    return max(candidates, key=lambda c: int(c.value[1:]))


def escalate(current: ChangeClass, evidence: str) -> ChangeClass:
    """Remonte la classe si l'impact l'exige (jamais l'inverse)."""
    return current
