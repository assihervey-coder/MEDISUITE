"""Expositions à risque — synthèse des segments de voyage."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.domain.travel.entities import TravelHistory
from tropirag.domain.travel.geography import get_profile, risk_level


@dataclass(slots=True)
class ExposureSummary:
    """Ce qui ressort du voyage, pertinent pour le différentiel."""

    countries: list[str] = field(default_factory=list)
    malaria_exposure: bool = False          # séjour zone paludéenne
    malaria_intensity: str = "none"          # max(geo.malaria)
    dengue_exposure: str = "none"           # niveau max
    yellow_fever_zone: bool = False
    lassa_zone: bool = False
    ebola_outbreak_zone: bool = False
    marburg_outbreak_zone: bool = False
    meningitis_belt: bool = False
    rural_stay: bool = False
    forest_stay: bool = False
    stagnant_water: bool = False            # leptospirose
    livestock_contact: bool = False
    sick_contacts: bool = False
    burial_attended: bool = False           # MVH
    unprotected: bool = False               # pas de chimioprophylaxie en zone palu
    yf_unvaccinated: bool = False           # en zone fièvre jaune sans vaccin
    typhoid_xdr_zone: bool = False          # V1.2 — voyage zone foyer typhoïde XDR

    def as_dict(self) -> dict:
        return {
            "countries": self.countries,
            "malaria_exposure": self.malaria_exposure,
            "malaria_intensity": self.malaria_intensity,
            "dengue_exposure": self.dengue_exposure,
            "yellow_fever_zone": self.yellow_fever_zone,
            "lassa_zone": self.lassa_zone,
            "ebola_outbreak_zone": self.ebola_outbreak_zone,
            "meningitis_belt": self.meningitis_belt,
            "rural_stay": self.rural_stay,
            "forest_stay": self.forest_stay,
            "stagnant_water": self.stagnant_water,
            "burial_attended": self.burial_attended,
            "unprotected_malaria": self.unprotected,
            "yf_unvaccinated_in_zone": self.yf_unvaccinated,
            "typhoid_xdr_zone": self.typhoid_xdr_zone,
        }


def summarize_exposures(travel: TravelHistory) -> ExposureSummary:
    s = ExposureSummary(countries=travel.countries_visited())
    for seg in travel.segments:
        g = get_profile(seg.country)
        if seg.rural_stay:
            s.rural_stay = True
        if seg.forest_stay:
            s.forest_stay = True
        s.stagnant_water |= seg.stagnant_water
        s.livestock_contact |= seg.livestock_contact
        s.sick_contacts |= seg.sick_contacts
        s.burial_attended |= seg.burial_attended
        if g.malaria in ("high", "moderate"):
            s.malaria_exposure = True
            if g.malaria == "high":
                s.malaria_intensity = "high"
            elif s.malaria_intensity != "high":
                s.malaria_intensity = "moderate"
            if not seg.chemoprophylaxis_taken:
                s.unprotected = True
        d = risk_level(seg.country, "dengue", seg.region)
        if d in ("high", "moderate", "outbreak"):
            s.dengue_exposure = "high" if d == "outbreak" else d
        if g.yellow_fever == "high":
            s.yellow_fever_zone = True
            if not travel.vaccinations.yellow_fever_certified:
                s.yf_unvaccinated = True
        if g.lassa == "high":
            s.lassa_zone = True
        if g.ebola == "outbreak":
            s.ebola_outbreak_zone = True
        if g.marburg == "outbreak":
            s.marburg_outbreak_zone = True
        s.meningitis_belt |= g.meningitis_belt
        # V1.2 — typhoïde XDR : foyer Asie du Sud (Pakistan au premier plan)
        if getattr(g, "typhoid_xdr", "none") in ("high", "outbreak"):
            s.typhoid_xdr_zone = True
    return s
