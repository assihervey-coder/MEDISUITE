"""Événements API — flux des événements émis (arbre conforme)."""
from __future__ import annotations

import importlib

from fastapi import APIRouter

from ..._bridge import register

register()

_events = importlib.import_module("ecp.domain.proposal.events")

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events(limit: int = 100) -> list[dict]:
    return _events.EVENTS_EMITTED[-limit:]
