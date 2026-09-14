"""Schéma API voyage (dict validé par TravelHistory.from_dict)."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class TravelIn(BaseModel):
    segments: list[dict[str, Any]] = []
    vaccinations: dict[str, Any] = {}
    resident_country: str = "CI"
