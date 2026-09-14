"""Escalade de santé publique."""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.clinical_engine.public_health.notification import notification_for


@dataclass(slots=True)
class PublicHealthEscalation:
    required: bool
    notifications: list[dict]


def escalate_to_public_health(diseases: list[str]) -> PublicHealthEscalation:
    notifs = []
    for d in diseases:
        n = notification_for(d)
        if n:
            notifs.append(n.to_dict())
    return PublicHealthEscalation(required=bool(notifs), notifications=notifs)
