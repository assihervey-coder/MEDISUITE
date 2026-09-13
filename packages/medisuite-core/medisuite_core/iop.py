"""Profils FHIR nationaux IOP-CI — validation et catalogue (ADR-0024). v0.5.

Implémente les contraintes des profils candidats Côte d'Ivoire :
- identifiant national de santé (OID 2.16.840.1.113883.2.8.8.10.10),
  alphanumérique 10-16 sans séparateur (`^[A-Z0-9]{10,16}$`) ;
- CNAM secondaire (10 chiffres) ;
- région sanitaire parmi les 13 régions administratives ;
- catalogue des StructureDefinition servies par le hub.

Zéro dépendance : fonctions pures testables sans serveur FHIR.
"""
from __future__ import annotations

import re
from typing import Any

NATIONAL_OID = "urn:oid:2.16.840.1.113883.2.8.8.10.10"
CNAM_SYSTEM = "urn:medisuite:cnam"
PROFILE_PATIENT = "http://medisuite.ci/fhir/StructureDefinition/Patient-CI-IOP"
PROFILE_OBSERVATION = ("http://medisuite.ci/fhir/StructureDefinition/"
                       "Observation-CI-IOP")

_NATIONAL_RE = re.compile(r"^[A-Z0-9]{10,16}$")
_CNAM_RE = re.compile(r"^\d{10}$")

# Liste de RÉFÉRENCE partielle (17 régions sur 31 + 2 districts autonomes
# du découpage administratif ivoirien) — À COMPLÉTER avant production avec
# la liste officielle MoH/HCP (ADR-0024 §conséquences). La validation
# refusera toute région absente : fail-closed jusqu'à confirmation.
REGIONS_SANITAIRES = (
    "Abidjan", "Bas-Sassandra", "Comoé", "Denguélé", "Gôh-Djiboua",
    "Lacs", "Lagunes", "Montagnes", "Sassandra-Marahoué", "Savanes",
    "Vallée du Bandama", "Woroba", "Yamoussoukro", "Iffou", "Moronou",
    "Bélier", "N'Zi",
)

PROFILES = (
    {
        "id": "Patient-CI-IOP",
        "url": PROFILE_PATIENT,
        "version": "0.5.0",
        "status": "draft-candidate",
        "description": "Patient ivoirien : identifiant national obligatoire, "
                       "CNAM secondaire, région sanitaire (ADR-0024)",
        "file": "StructureDefinition-Patient-CI-IOP.json",
    },
    {
        "id": "Observation-CI-IOP",
        "url": PROFILE_OBSERVATION,
        "version": "0.5.0",
        "status": "draft-candidate",
        "description": "Observation laboratoire : LOINC/UCUM obligatoires, "
                       "sujet Patient-CI-IOP (ADR-0024)",
        "file": "StructureDefinition-Observation-CI-IOP.json",
    },
    {
        "id": "CodeSystem-CI-identifiants",
        "url": "http://medisuite.ci/fhir/CodeSystem/CI-identifiants",
        "version": "0.5.0",
        "status": "draft-candidate",
        "description": "Systèmes d'identifiants nationaux (candidat)",
        "file": "CodeSystem-CI-identifiants.json",
    },
    {
        "id": "ValueSet-CI-identifiants",
        "url": "http://medisuite.ci/fhir/ValueSet/CI-identifiants",
        "version": "0.5.0",
        "status": "draft-candidate",
        "description": "ValueSet des identifiants acceptés (slicing)",
        "file": "ValueSet-CI-identifiants.json",
    },
)


class IopValidationError(ValueError):
    """Ressource non conforme aux profils IOP-CI (ADR-0024)."""


def validate_national_id(value: str) -> str:
    """Valide un identifiant national de santé (10-16 alphanumériques maj.)."""
    v = (value or "").strip().upper()
    if not _NATIONAL_RE.match(v):
        raise IopValidationError(
            f"identifiant national invalide : '{value}' (attendu 10-16 "
            "caractères alphanumériques majuscules, sans séparateur)")
    return v


def validate_cnam(value: str) -> str:
    """Valide un numéro d'affilié CNAM (10 chiffres)."""
    v = (value or "").strip()
    if not _CNAM_RE.match(v):
        raise IopValidationError(
            f"numéro CNAM invalide : '{value}' (attendu 10 chiffres)")
    return v


def validate_region(region: str) -> str:
    """Valide la région sanitaire contre la liste administrative."""
    if region not in REGIONS_SANITAIRES:
        raise IopValidationError(
            f"région sanitaire inconnue : '{region}' "
            f"(attendue parmi {len(REGIONS_SANITAIRES)} régions)")
    return region


def patient_to_iop(p: dict) -> dict:
    """Mapping Patient MEDISUITE → Patient-CI-IOP (base fhir.py + contraintes).

    Exigences : `identifiant_national` (ou `numero_dossier` format national)
    obligatoire ; `cnam` optionnel validé ; `region` optionnelle validée.
    """
    from . import fhir as fhir_mod

    national = p.get("identifiant_national") or p.get("numero_dossier", "")
    national = validate_national_id(str(national))
    resource = fhir_mod.patient_to_fhir(p)
    identifiers = [{"system": NATIONAL_OID, "value": national,
                    "use": "official"}]
    if p.get("cnam"):
        identifiers.append({"system": CNAM_SYSTEM,
                            "value": validate_cnam(str(p["cnam"]))})
    resource["identifier"] = identifiers
    resource.setdefault("meta", {})["profile"] = [PROFILE_PATIENT]
    if p.get("region"):
        region = validate_region(p["region"])
        resource.setdefault("extension", []).append({
            "url": "http://medisuite.ci/fhir/StructureDefinition/region-sanitaire",
            "valueString": region,
        })
    return resource


def catalog() -> list[dict[str, Any]]:
    """Catalogue des profils servis par le hub (endpoint /api/v1/fhir/profiles)."""
    return [dict(p) for p in PROFILES]
