"""Santé des gateways — ping consolidé."""
from __future__ import annotations

from typing import Protocol


class HasName(Protocol):
    name: str


def ping_all(gateways: list) -> dict[str, bool]:
    """Ping chaque gateway — {nom: dispo}."""
    out: dict[str, bool] = {}
    for gw in gateways:
        try:
            out[gw.name] = bool(gw.is_available("ping"))
        except Exception:  # noqa: BLE001
            out[gw.name] = False
    return out
