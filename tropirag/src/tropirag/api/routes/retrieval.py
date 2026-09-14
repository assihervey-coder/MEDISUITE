"""Routes retrieval bas-niveau (diagnostic du RAG)."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RetrievalDebug(BaseModel):
    query: str
    channel: str = "hybrid"   # bm25 | vector | hybrid


@router.post("/retrieval/search")
async def search(req: RetrievalDebug) -> dict:
    from tropirag.evidence_engine.evidence_engine import EvidenceEngine

    ee = EvidenceEngine()
    if not ee.loaded:
        ee.load()
    if req.channel == "bm25":
        hits = ee.hybrid.bm25.search(req.query, 10)
        return {"channel": "bm25", "hits": [{"unit_id": u, "score": s} for u, s in hits]}
    if req.channel == "vector":
        hits = ee.hybrid.vectors.search(req.query, 10)
        return {"channel": "vector", "hits": [{"unit_id": u, "score": s} for u, s in hits]}
    results = ee.hybrid.retrieve(req.query, 10)
    return {"channel": "hybrid",
            "hits": [{"unit_id": r.unit_id, "rrf": r.rrf_score,
                      "bm25_rank": r.bm25_rank, "vector_rank": r.vector_rank}
                     for r in results]}
