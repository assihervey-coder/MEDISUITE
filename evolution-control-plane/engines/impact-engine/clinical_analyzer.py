"""Analyseur clinique — règles cliniques et modules spécialité touchés."""
from __future__ import annotations

from pathlib import Path

RULES_DIR = Path(__file__).resolve().parents[3] / "packages" / "clinical-rules" / "medisuite_rules"


def count_clinical_rules() -> int:
    """Nombre de modules de règles (proxy déterministe du périmètre clinique)."""
    if not RULES_DIR.exists():
        return 0
    return len([p for p in RULES_DIR.glob("*.py") if p.name != "__init__.py"])


def analyze_clinical(changed_paths: list[str]) -> dict:
    rules_touched = [p for p in changed_paths if p.startswith("packages/clinical-rules/")]
    specialties = sorted({p.split("/")[1] for p in changed_paths
                          if p.startswith("services/")
                          and p.split("/")[1].endswith("-service")
                          and p.split("/")[1] not in
                          {"api-gateway", "auth-service", "patient-service",
                           "imaging-service", "laboratory-service", "ecrf-service",
                           "reporting-service", "notification-service",
                           "audit-service", "integration-service",
                           "analytics-service", "dicom-gateway", "hl7-gateway",
                           "multimodal-gateway", "explainability-service"}})
    return {
        "clinical_rules_touched": rules_touched,
        "rule_modules": count_clinical_rules(),
        "specialty_services": specialties,
        "count": len(rules_touched) + len(specialties),
    }
