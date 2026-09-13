"""Schémas Pydantic — assessment/decision/change/validation/rollout/rollback.

Arbre conforme : les modules frères réexportent les modèles partagés.
"""
from .proposal import DecisionIn, ProposalIn  # noqa: F401
from pydantic import BaseModel, Field


class AssessIn(BaseModel):
    changed_paths: list[str] = []
    impacts: dict[str, str] = {}
    breaking: bool = False
    cross_domain: bool = False


class ChangeSetIn(BaseModel):
    proposal_id: str
    baseline_version: str
    baseline_commit: str
    target_version: str
    units: list[dict] = []
    migration_required: bool = False


class ValidationIn(BaseModel):
    facts: dict = {}


class RolloutIn(BaseModel):
    change_class: str = "P4"
    checkpoints: dict[str, str] = {}


class RollbackIn(BaseModel):
    metrics: dict[str, float] = {}
    alerts: list[str] = []
    human_decision: bool = False
    checkpoints_restored: list[str] = []
