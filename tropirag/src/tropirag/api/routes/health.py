"""Route santé système."""
from __future__ import annotations

from fastapi import APIRouter

from tropirag.observability.health import system_health

router = APIRouter()

_HEALTH = {"rules": None, "units": None}


def prime(rules: int, units: int) -> None:
    _HEALTH.update(rules=rules, units=units)


@router.get("/health")
async def health() -> dict:
    from tropirag.core.config import get_config

    cfg = get_config()
    if _HEALTH["rules"] is None:
        try:
            from tropirag.clinical_engine.rules.rule_loader import load_rule_engine
            from tropirag.evidence_engine.evidence_engine import EvidenceEngine

            _HEALTH["rules"] = load_rule_engine().count()
            _HEALTH["units"] = EvidenceEngine().load()
        except Exception:  # noqa: BLE001
            _HEALTH["rules"], _HEALTH["units"] = 0, 0
    return system_health(_HEALTH["rules"] or 0, _HEALTH["units"] or 0,
                         cfg.inference.mode)
