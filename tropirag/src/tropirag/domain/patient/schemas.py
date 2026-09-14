"""Schémas Pydantic Patient (bordure API)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from tropirag.core.enums import PregnancyStatus, Sex


class PatientIn(BaseModel):
    patient_id: str | None = None
    age_years: int | None = Field(default=None, ge=0, le=120)
    age_months: int | None = Field(default=None, ge=0)
    sex: Sex = Sex.UNKNOWN
    pregnant: PregnancyStatus = PregnancyStatus.NOT_APPLICABLE
    weight_kg: float | None = Field(default=None, ge=0.5, le=300)
    known_allergies: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    birthdate: str | None = None


class PatientOut(BaseModel):
    age_years: int | None = None
    sex: Sex = Sex.UNKNOWN
    pregnant: PregnancyStatus = PregnancyStatus.NOT_APPLICABLE
    is_child: bool = False
    is_infant: bool = False
    is_pregnant_or_possible: bool = False
