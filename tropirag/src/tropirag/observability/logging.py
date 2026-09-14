"""Logging structuré JSON — logs sans PII (redaction systématique)."""
from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("case_id", "request_id", "model_id", "step", "event"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)[:400]
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO", fmt: str = "json") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    root = logging.getLogger("tropirag")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if fmt == "json" else
                          logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"tropirag.{name}")
