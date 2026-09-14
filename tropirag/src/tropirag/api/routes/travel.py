"""Routes voyage : expositions et géographie."""
from __future__ import annotations

from fastapi import APIRouter

from tropirag.domain.travel.geography import get_profile, risk_level
from tropirag.domain.travel.entities import TravelHistory

router = APIRouter()


@router.get("/travel/profile/{iso}")
async def profile(iso: str) -> dict:
    p = get_profile(iso)
    return {"iso": p.iso, "name_fr": p.name_fr, "name_en": p.name_en,
            "malaria": p.malaria, "dengue": p.dengue,
            "yellow_fever": p.yellow_fever, "lassa": p.lassa, "ebola": p.ebola,
            "meningitis_belt": p.meningitis_belt}


@router.post("/travel/exposures")
async def exposures(travel: dict) -> dict:
    from tropirag.domain.travel.exposures import summarize_exposures

    th = TravelHistory.from_dict(travel)
    return summarize_exposures(th).as_dict()
