"""Santé des modèles du mesh — circuit breaker + ping périodique."""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass(slots=True)
class HealthRecord:
    model_id: str
    state: str = "unknown"        # unknown | up | down
    consecutive_failures: int = 0
    last_check: float = 0.0
    last_error: str | None = None
    latency_ms: float | None = None


class ModelHealthMonitor:
    """Circuit breaker simple : N échecs consécutifs → down, reset après T."""

    def __init__(self, failure_threshold: int = 3, reset_seconds: float = 300.0) -> None:
        self._threshold = failure_threshold
        self._reset = reset_seconds
        self._records: dict[str, HealthRecord] = {}

    def report_success(self, model_id: str, latency_ms: float | None = None) -> None:
        r = self._records.setdefault(model_id, HealthRecord(model_id))
        r.state, r.consecutive_failures = "up", 0
        r.last_check, r.latency_ms = time.time(), latency_ms
        r.last_error = None

    def report_failure(self, model_id: str, error: str) -> None:
        r = self._records.setdefault(model_id, HealthRecord(model_id))
        r.consecutive_failures += 1
        r.last_check, r.last_error = time.time(), error
        if r.consecutive_failures >= self._threshold:
            r.state = "down"

    def is_up(self, model_id: str) -> bool:
        r = self._records.get(model_id)
        if r is None:
            return False
        if r.state == "down" and time.time() - r.last_check > self._reset:
            r.state, r.consecutive_failures = "unknown", 0
        return r.state == "up"

    def status(self, model_id: str) -> HealthRecord:
        return self._records.get(model_id, HealthRecord(model_id))

    def snapshot(self) -> dict[str, dict]:
        return {mid: {"state": r.state, "failures": r.consecutive_failures,
                     "latency_ms": r.latency_ms} for mid, r in self._records.items()}
