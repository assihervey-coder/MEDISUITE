"""Bus d'événements interne : publication/souscription par topic + sink JSONL.

En production, ce bus est adossé à Kafka (spec : services/*/events/publisher.py).
En dev, un sink JSONL suffit pour la traçabilité inter-services.
"""
from __future__ import annotations

import json
import pathlib
import threading
import time
from collections import defaultdict
from typing import Callable

from .db import ROOT

_SINK = ROOT / "data" / "events.jsonl"
_lock = threading.Lock()


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[dict], None]) -> None:
        self._subscribers[topic].append(handler)

    def publish(self, topic: str, payload: dict) -> dict:
        event = {"topic": topic, "timestamp": time.time(), "payload": payload}
        with _lock:
            _SINK.parent.mkdir(exist_ok=True)
            with open(_SINK, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        for handler in self._subscribers.get(topic, []):
            try:
                handler(payload)
            except Exception as exc:  # un subscriber défaillant ne casse pas le bus
                event.setdefault("errors", []).append(str(exc))
        return event


bus = EventBus()

TOPICS = {
    "patient.created": "un dossier patient est créé",
    "patient.updated": "démographie modifiée (→ ADT^A08)",
    "lab.ordered": "prescription d'analyses (→ ORM^O01)",
    "lab.result.validated": "résultat validé (→ ORU^R01 + notification si critique)",
    "imaging.study.received": "examen DICOM reçu (STOW-RS)",
    "imaging.report.signed": "compte-rendu signé",
    "ai.inference.completed": "inférence IA terminée (→ explicabilité + audit)",
    "appointment.scheduled": "RDV programmé (→ SIU^S12)",
    "alert.clinical": "alerte clinique (sepsis, valeur critique, risque suicidaire)",
}
