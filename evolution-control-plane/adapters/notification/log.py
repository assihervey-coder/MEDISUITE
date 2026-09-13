"""Adaptateur notification — V1 : log structuré (arbre conforme)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def notify(event: str, severity: str = "info", **payload) -> dict:
    record = {"notification": event, "severity": severity,
              "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              **payload}
    print(json.dumps(record, ensure_ascii=False), file=sys.stderr)
    return record
