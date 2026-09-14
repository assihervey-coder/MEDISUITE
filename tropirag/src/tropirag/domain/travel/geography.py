"""Géographie clinique — Afrique de l'Ouest : endémicités et risques par pays.

Sources des niveaux : profils OMS/CDC par pays (résumés opérationnels — les
règles YAML citent les evidence_units correspondantes).
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Niveaux : 'high' | 'moderate' | 'low' | 'none' | 'outbreak' (épidémie active déclarée)


@dataclass(slots=True)
class CountryProfile:
    """Alias historique — utiliser GeoProfile."""

    iso: str
    name_fr: str
    name_en: str
    malaria: str = "high"
    dengue: str = "moderate"
    yellow_fever: str = "high"
    lassa: str = "low"
    ebola: str = "none"
    meningitis_belt: bool = False
    regions: dict[str, dict] = field(default_factory=dict)


@dataclass(slots=True)
class GeoProfile:
    """Profil géographique de risque (version propre)."""

    iso: str
    name_fr: str
    name_en: str
    malaria: str = "high"
    dengue: str = "moderate"
    yellow_fever: str = "high"
    lassa: str = "low"
    ebola: str = "none"
    marburg: str = "none"
    meningitis_belt: bool = False
    cholera_risk: str = "low"
    typhoid_xdr: str = "none"   # foyer typhoïde XDR (S. Typhi résistante extrême)
    regions: dict[str, dict[str, str]] = field(default_factory=dict)


_PROFILES: dict[str, GeoProfile] = {
    "CI": GeoProfile("CI", "Côte d'Ivoire", "Ivory Coast",
                     malaria="high", dengue="moderate", yellow_fever="high",
                     lassa="low", meningitis_belt=False,
                     regions={
                         "abidjan": {"dengue": "high"},
                         "bas-sassandra": {"dengue": "high"},
                         "sud-comoe": {"malaria": "high"},
                     }),
    "BF": GeoProfile("BF", "Burkina Faso", "Burkina Faso",
                     malaria="high", dengue="low", yellow_fever="moderate",
                     lassa="none", meningitis_belt=True),
    "GH": GeoProfile("GH", "Ghana", "Ghana",
                     malaria="high", dengue="moderate", yellow_fever="high", lassa="low"),
    "GN": GeoProfile("GN", "Guinée", "Guinea",
                     malaria="high", dengue="moderate", yellow_fever="high",
                     lassa="high", ebola="outbreak"),
    "SL": GeoProfile("SL", "Sierra Leone", "Sierra Leone",
                     malaria="high", dengue="moderate", yellow_fever="high", lassa="high"),
    "LR": GeoProfile("LR", "Liberia", "Liberia",
                     malaria="high", dengue="moderate", yellow_fever="high", lassa="high"),
    "ML": GeoProfile("ML", "Mali", "Mali",
                     malaria="high", dengue="low", yellow_fever="moderate",
                     meningitis_belt=True),
    "SN": GeoProfile("SN", "Sénégal", "Senegal",
                     malaria="low", dengue="moderate", yellow_fever="moderate",
                     regions={"sedhiou": {"malaria": "moderate"}}),
    "TG": GeoProfile("TG", "Togo", "Togo",
                     malaria="high", dengue="moderate", yellow_fever="high"),
    "BJ": GeoProfile("BJ", "Bénin", "Benin",
                     malaria="high", dengue="moderate", yellow_fever="high"),
    "NE": GeoProfile("NE", "Niger", "Niger",
                     malaria="moderate", dengue="low", yellow_fever="moderate",
                     meningitis_belt=True),
    "NG": GeoProfile("NG", "Nigéria", "Nigeria",
                     malaria="high", dengue="moderate", yellow_fever="high", lassa="high"),
    "CM": GeoProfile("CM", "Cameroun", "Cameroon",
                     malaria="high", dengue="moderate", yellow_fever="high"),
    "CD": GeoProfile("CD", "RD Congo", "DR Congo",
                     malaria="high", dengue="moderate", yellow_fever="high",
                     ebola="outbreak"),
    "GA": GeoProfile("GA", "Gabon", "Gabon",
                     malaria="high", dengue="moderate", yellow_fever="high"),
    "CG": GeoProfile("CG", "Congo", "Congo",
                     malaria="high", dengue="moderate", yellow_fever="high"),
    "GQ": GeoProfile("GQ", "Guinée équatoriale", "Equatorial Guinea",
                     malaria="high", dengue="moderate", yellow_fever="high",
                     marburg="outbreak"),
    "UG": GeoProfile("UG", "Ouganda", "Uganda",
                     malaria="high", dengue="moderate", yellow_fever="high",
                     ebola="outbreak"),
    # V1.2 — foyer typhoïde XDR (Salmonella Typhi résistante extrême) : Asie du Sud.
    # Sources : CDC/OMS — épidémie XDR au Pakistan (2016→), diffusion régionale.
    "PK": GeoProfile("PK", "Pakistan", "Pakistan",
                     malaria="moderate", dengue="low", yellow_fever="none",
                     typhoid_xdr="outbreak"),
    "IN": GeoProfile("IN", "Inde", "India",
                     malaria="moderate", dengue="high", yellow_fever="none",
                     typhoid_xdr="high"),
    "AF": GeoProfile("AF", "Afghanistan", "Afghanistan",
                     malaria="moderate", dengue="low", yellow_fever="none",
                     typhoid_xdr="high"),
}

# Pays hors région — profil générique prudent
_DEFAULT = GeoProfile("XX", "International", "International",
                      malaria="unknown", dengue="unknown", yellow_fever="unknown")

_LEVEL_RANK = {"none": 0, "low": 1, "moderate": 2, "high": 3, "outbreak": 4, "unknown": 2}


def get_profile(iso: str) -> GeoProfile:
    return _PROFILES.get(str(iso or "").upper()[:2], _DEFAULT)


def risk_level(iso: str, disease: str, region: str | None = None) -> str:
    """Niveau de risque pour une maladie dans un pays (éventuellement affiné par région)."""
    p = get_profile(iso)
    level = getattr(p, disease, "unknown")
    if region and p.regions:
        reg = p.regions.get(_norm_region(region))
        if reg and disease in reg:
            level = reg[disease]
    return level


def max_risk_countries(countries: list[str], disease: str) -> tuple[str, str]:
    """Renvoie (pays, niveau) au risque max pour la maladie donnée."""
    best_iso, best_lvl = "", "none"
    for c in countries:
        lvl = risk_level(c, disease)
        if _LEVEL_RANK.get(lvl, 0) > _LEVEL_RANK.get(best_lvl, 0):
            best_iso, best_lvl = c, lvl
    return best_iso, best_lvl


def malaria_endemic_countries(countries: list[str]) -> list[str]:
    return [c for c in countries if _LEVEL_RANK.get(risk_level(c, "malaria"), 0) >= 2]


def _norm_region(r: str) -> str:
    import re
    import unicodedata

    t = unicodedata.normalize("NFKD", r.lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


COUNTRY_NAMES_FR = {p.iso: p.name_fr for p in _PROFILES.values()}
