"""Routes d'audit."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/audit")
async def recent_audit(limit: int = 50) -> dict:
    from tropirag.persistence.database import Database
    from tropirag.persistence.repositories.audit_repository import AuditRepository

    repo = AuditRepository(Database.instance())
    return {"events": repo.recent(limit)}


@router.get("/audit/metrics")
async def audit_metrics() -> dict:
    from tropirag.observability.metrics import Metrics

    return Metrics.instance().snapshot()
