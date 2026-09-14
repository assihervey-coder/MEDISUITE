"""Table ORM `inferences` — journal des appels du mesh IA par cas."""
from __future__ import annotations

import time

from tropirag.persistence.models.base import Column

INFERENCE_TABLE = "inferences"

INFERENCE_COLUMNS = [
    Column("inference_id", "TEXT", primary_key=True),
    Column("case_id", "TEXT", index=True),
    Column("model_id", "TEXT", index=True),
    Column("task", "TEXT"),
    Column("mode", "TEXT", default="deterministic"),
    Column("status", "TEXT"),                  # ok | refused | degraded | error
    Column("latency_ms", "REAL"),
    Column("detail", "TEXT"),
    Column("created_at", "TEXT"),
]


def row_from_inference(case_id: str, model_id: str, task: str,
                       status: str = "ok", latency_ms: float | None = None,
                       mode: str = "deterministic", detail: str = "",
                       created_at: str | None = None) -> dict:
    return {
        "inference_id": f"inf-{case_id}-{model_id}-{task}",
        "case_id": case_id, "model_id": model_id, "task": task,
        "mode": mode, "status": status, "latency_ms": latency_ms,
        "detail": detail,
        "created_at": created_at or time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def to_domain(row) -> dict:
    return dict(row)
