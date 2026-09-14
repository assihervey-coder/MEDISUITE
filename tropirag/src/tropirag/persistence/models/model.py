"""Table ORM `models_registry` — snapshot SQL du mesh IA (Model Registry)."""
from __future__ import annotations

import json

from tropirag.persistence.models.base import Column

MODEL_TABLE = "models_registry"

MODEL_COLUMNS = [
    Column("model_id", "TEXT", primary_key=True),
    Column("display_name", "TEXT"),
    Column("family", "TEXT", index=True),
    Column("gateway", "TEXT"),
    Column("vram_gb", "REAL"),
    Column("priority", "INTEGER"),
    Column("deployment", "TEXT"),
    Column("clinically_validated", "INTEGER", default=0),
    Column("capabilities_json", "TEXT"),
    Column("health", "TEXT", default="unknown"),
]


def row_from_model_meta(m) -> dict:
    """ModelMetadata → ligne models."""
    caps = m.capabilities
    return {
        "model_id": m.model_id,
        "display_name": m.display_name,
        "family": m.family,
        "gateway": m.provider_gateway,
        "vram_gb": m.vram_gb,
        "priority": m.priority,
        "deployment": m.deployment,
        "clinically_validated": 1 if m.clinically_validated else 0,
        "capabilities_json": json.dumps({
            "tasks": [t.value for t in caps.tasks],
            "languages": caps.languages,
            "clinical_risk_max": caps.clinical_risk_max,
            "autonomous_diagnosis": caps.autonomous_diagnosis_allowed,
            "evidence_required": caps.evidence_required,
        }, ensure_ascii=False),
        "health": m.health,
    }


def to_domain(row) -> dict:
    return {
        "model_id": row["model_id"], "display_name": row["display_name"],
        "family": row["family"], "gateway": row["gateway"],
        "vram_gb": row["vram_gb"], "priority": row["priority"],
        "clinically_validated": bool(row["clinically_validated"]),
        "capabilities": json.loads(row["capabilities_json"] or "{}"),
        "health": row["health"],
    }
