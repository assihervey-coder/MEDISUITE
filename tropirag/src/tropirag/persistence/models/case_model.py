"""Modèle de persistance des cas."""
from __future__ import annotations

import json
import time


def row_from_case(case_id: str, patient: dict, payload: dict) -> dict:
    return {"case_id": case_id, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "patient_json": json.dumps(patient, ensure_ascii=False),
            "payload_json": json.dumps(payload, ensure_ascii=False)}
