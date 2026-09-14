"""Métriques en mémoire — exportables Prometheus-texte."""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock


class Metrics:
    _instance = None

    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    @classmethod
    def instance(cls) -> "Metrics":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def inc(self, name: str, value: float = 1.0, **labels: str) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._counters[key] += value

    def observe(self, name: str, value: float, **labels: str) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._histograms[key].append(value)
            if len(self._histograms[key]) > 2000:
                self._histograms[key] = self._histograms[key][-1000:]

    def snapshot(self) -> dict:
        with self._lock:
            out = {"counters": dict(self._counters)}
            for k, vals in self._histograms.items():
                if vals:
                    v = sorted(vals)
                    out[k + "_p50"] = v[len(v) // 2]
                    out[k + "_p95"] = v[int(len(v) * 0.95)]
            return out

    @staticmethod
    def _key(name: str, labels: dict[str, str]) -> str:
        if not labels:
            return name
        tag = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{tag}}}"


def prometheus_export() -> str:
    m = Metrics.instance()
    lines = []
    for k, v in sorted(m.snapshot().items()):
        if "{" in k:
            name, tag = k.split("{", 1)
            lines.append(f'{name}{tag.replace("}", "")} {v}')
        else:
            lines.append(f"{k} {v}")
    return "\n".join(lines) + "\n"


def track_pipeline(stage: str, duration_ms: float) -> None:
    Metrics.instance().observe(f"tropirag_stage_ms", duration_ms, stage=stage)
    Metrics.instance().inc(f"tropirag_stage_total", 1.0, stage=stage)
