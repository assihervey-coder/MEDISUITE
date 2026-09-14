"""Entités voyage et expositions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from tropirag.core.datetime import parse_date_flexible


@dataclass(slots=True)
class TravelSegment:
    """Un segment de voyage : pays/région, dates, contexte."""

    country: str                  # code ISO 'CI', 'GH', 'SN', 'BF', 'ML', 'GN', 'TG', 'BJ', 'NG', 'LR', 'SL'...
    region: str | None = None     # région/prefecture/province
    arrival: date | None = None
    departure: date | None = None  # retour dans le pays de résidence
    purpose: str | None = None    # tourisme, famille, travail, humanitaire
    rural_stay: bool = False
    forest_stay: bool = False     # zone forestière (arboviroses, leptospirose)
    stagnant_water: bool = False  # contact eaux stagnantes
    livestock_contact: bool = False
    sick_contacts: bool = False   # contacts avec malades
    burial_attended: bool = False  # participation à des funérailles (MVH)
    mosquito_protection: bool = False
    chemoprophylaxis_taken: bool = False
    details: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "TravelSegment":
        return cls(
            country=str(d.get("country", "")).upper()[:2] or "XX",
            region=d.get("region"),
            arrival=parse_date_flexible(d.get("arrival")),
            departure=parse_date_flexible(d.get("departure")),
            purpose=d.get("purpose"),
            rural_stay=bool(d.get("rural_stay", False)),
            forest_stay=bool(d.get("forest_stay", False)),
            stagnant_water=bool(d.get("stagnant_water", False)),
            livestock_contact=bool(d.get("livestock_contact", False)),
            sick_contacts=bool(d.get("sick_contacts", False)),
            burial_attended=bool(d.get("burial_attended", False)),
            mosquito_protection=bool(d.get("mosquito_protection", False)),
            chemoprophylaxis_taken=bool(d.get("chemoprophylaxis_taken", False)),
            details=dict(d.get("details") or {}),
        )

    def contains(self, d: date) -> bool:
        a = self.arrival or date.min
        b = self.departure or date.max
        return a <= d <= b


@dataclass(slots=True)
class Vaccination:
    """Vaccinations pertinentes fièvre+voyage."""

    yellow_fever_date: date | None = None
    yellow_fever_certified: bool = False
    hepatitis_a_date: date | None = None
    typhoid_date: date | None = None
    meningococcal_date: date | None = None

    @classmethod
    def from_dict(cls, d: dict | None) -> "Vaccination":
        d = d or {}
        return cls(
            yellow_fever_date=parse_date_flexible(d.get("yellow_fever_date")),
            yellow_fever_certified=bool(d.get("yellow_fever_certified", False)),
            hepatitis_a_date=parse_date_flexible(d.get("hepatitis_a_date")),
            typhoid_date=parse_date_flexible(d.get("typhoid_date")),
            meningococcal_date=parse_date_flexible(d.get("meningococcal_date")),
        )


@dataclass(slots=True)
class TravelHistory:
    """Historique complet des voyages + vaccinations."""

    segments: list[TravelSegment] = field(default_factory=list)
    vaccinations: Vaccination = field(default_factory=Vaccination)
    resident_country: str = "CI"

    @classmethod
    def from_dict(cls, d: dict | None) -> "TravelHistory":
        d = d or {}
        segs = [TravelSegment.from_dict(s) for s in d.get("segments", [])]
        return cls(
            segments=segs,
            vaccinations=Vaccination.from_dict(d.get("vaccinations")),
            resident_country=str(d.get("resident_country", "CI")).upper()[:2],
        )

    def last_return(self) -> date | None:
        deps = [s.departure for s in self.segments if s.departure]
        return max(deps) if deps else None

    def countries_visited(self) -> list[str]:
        seen: list[str] = []
        for s in self.segments:
            if s.country not in seen:
                seen.append(s.country)
        return seen

    def segments_active_at(self, d: date) -> list[TravelSegment]:
        return [s for s in self.segments if s.contains(d)]
