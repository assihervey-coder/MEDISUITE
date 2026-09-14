"""Routes preuves : interrogation du corpus."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class EvidenceQuery(BaseModel):
    query: str
    diseases: list[str] | None = None
    top_k: int = 5


@router.post("/evidence/query")
async def query_evidence(req: EvidenceQuery) -> dict:
    from tropirag.evidence_engine.evidence_engine import EvidenceEngine

    ee = EvidenceEngine()
    if not ee.loaded:
        ee.load()
    pack = ee.retrieve_evidence(req.query, diseases=req.diseases, top_k=req.top_k)
    return {
        "summary": pack.summary(),
        "results": [
            {"unit_id": u.unit_id, "citation": u.citation(),
             "authority": u.source.authority.value,
             "score": pack.scores.get(u.unit_id),
             "text": u.text[:500]}
            for u in pack.top(req.top_k)
        ],
    }


@router.get("/evidence/stats")
async def evidence_stats() -> dict:
    from tropirag.evidence_engine.evidence_engine import EvidenceEngine

    ee = EvidenceEngine()
    if not ee.loaded:
        ee.load()
    return ee.stats()
