"""Configuration DHIS2 — chargement YAML + surcharges environnement."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tropirag.core.config import TROPIRAG_ROOT

DEFAULT_CONFIG_PATH = TROPIRAG_ROOT / "configs" / "integrations" / "dhis2.yaml"


@dataclass(slots=True)
class DataElementSpec:
    de: str
    label: str = ""


@dataclass(slots=True)
class Dhis2Config:
    """Configuration d'export DHIS2 — placeholders MSP-CI documentés."""

    enabled: bool = True
    mode: str = "offline_queue"          # off | offline_queue | push
    base_url: str | None = None
    username: str | None = None
    password_env: str = "TROPIRAG_DHIS2_PASSWORD"
    timeout_s: float = 30.0
    verify_tls: bool = True
    org_unit: str = "OU-CI-PLACEHOLDER"
    period_strategy: str = "weekly"
    data_elements: dict[str, DataElementSpec] = field(default_factory=dict)
    category_option_combo: str = "default"
    queue_path: Path = TROPIRAG_ROOT / "runtime" / "state" / "dhis2_queue.json"
    queue_max_entries: int = 5000

    def data_element_uid(self, logical_key: str) -> str | None:
        spec = self.data_elements.get(logical_key)
        return spec.de if spec else None

    @classmethod
    def from_yaml(cls, path: str | Path | None = None) -> "Dhis2Config":
        p = Path(path) if path else DEFAULT_CONFIG_PATH
        raw: dict = {}
        if p.exists():
            with open(p, encoding="utf-8") as fh:
                raw = (yaml.safe_load(fh) or {}).get("dhis2") or {}

        server = raw.get("server") or {}
        ou = raw.get("organisation_unit") or {}
        period = raw.get("period") or {}
        queue = raw.get("queue") or {}

        elements: dict[str, DataElementSpec] = {}
        for key, spec in (raw.get("data_elements") or {}).items():
            if isinstance(spec, dict) and spec.get("de"):
                elements[str(key)] = DataElementSpec(str(spec["de"]),
                                                     str(spec.get("label", "")))

        cfg = cls(
            enabled=bool(raw.get("enabled", True)),
            mode=str(raw.get("mode", "offline_queue")),
            base_url=server.get("base_url"),
            username=server.get("username"),
            password_env=str(server.get("password_env", "TROPIRAG_DHIS2_PASSWORD")),
            timeout_s=float(server.get("timeout_s", 30)),
            verify_tls=bool(server.get("verify_tls", True)),
            org_unit=str(ou.get("default", "OU-CI-PLACEHOLDER")),
            period_strategy=str(period.get("strategy", "weekly")),
            data_elements=elements,
            category_option_combo=str(raw.get("category_option_combo", "default")),
            queue_path=TROPIRAG_ROOT / str(queue.get("path",
                                                     "runtime/state/dhis2_queue.json")),
            queue_max_entries=int(queue.get("max_entries", 5000)),
        )

        # --- surcharges environnementales ---------------------------------
        if v := os.environ.get("TROPIRAG_DHIS2_MODE"):
            cfg.mode = v
        if v := os.environ.get("TROPIRAG_DHIS2_BASE_URL"):
            cfg.base_url = v
        if v := os.environ.get("TROPIRAG_DHIS2_USERNAME"):
            cfg.username = v
        if v := os.environ.get("TROPIRAG_DHIS2_ORG_UNIT"):
            cfg.org_unit = v
        if v := os.environ.get("TROPIRAG_DHIS2_QUEUE_PATH"):
            cfg.queue_path = Path(v)
        return cfg

    @property
    def transport_ready(self) -> bool:
        return bool(self.base_url and self.username)


def load_dhis2_config(path: str | Path | None = None) -> Dhis2Config:
    return Dhis2Config.from_yaml(path)
