"""Risk Engine — scoring 0-100 + dimension spécialisées."""
from __future__ import annotations

from typing import Any

# réutilise le scoring du domaine (config risk-levels.yaml)
import importlib

from ..._bridge import register

register()
_risk = importlib.import_module("ecp.domain.assessment.risk")


def score(impacts: dict[str, str]) -> dict[str, Any]:
    rs = _risk.compute_risk(impacts)
    return {**rs.to_dict(), "weights": rs.weights}


def clinical_risk(patient_safety: str, clinical: str) -> str:
    """Dimension clinique : sécurité patient prime."""
    order = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
    return patient_safety if order[patient_safety] >= order[clinical] else clinical


def ai_risk(model_changed: bool, threshold_changed: bool,
            lineage_complete: bool) -> str:
    if threshold_changed and not lineage_complete:
        return "HIGH"
    if threshold_changed or model_changed:
        return "MEDIUM"
    return "LOW"


def security_risk(security_paths: int, network_policy: bool,
                  audit_chain: bool) -> str:
    if network_policy or audit_chain:
        return "HIGH"
    if security_paths:
        return "MEDIUM"
    return "LOW"


def regulatory_risk(compliance_paths: int, breaking: bool) -> str:
    if compliance_paths and breaking:
        return "HIGH"
    if compliance_paths or breaking:
        return "MEDIUM"
    return "LOW"
