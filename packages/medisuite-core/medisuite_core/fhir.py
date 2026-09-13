"""FHIR R4 — mapping des ressources cliniques fondamentales (ADR-0005).

Ressources supportées : Patient, Observation, Condition, Encounter, AllergyIntolerance.
Suffisant pour l'interopérabilité HIS/labo ; profils nationaux à ajouter en v0.2.
"""
from __future__ import annotations

from typing import Any


def _ref(resource_type: str, resource_id: str) -> dict:
    return {"reference": f"{resource_type}/{resource_id}"}


def patient_to_fhir(p: dict) -> dict:
    """dict patient MEDISUITE → FHIR R4 Patient."""
    names = [{"family": p.get("nom", ""), "given": [p.get("prenoms", "")]}]
    identifiers = [{
        "system": "urn:oid:2.16.840.1.113883.2.8.8.10.10",  # identifiant patient CI (exemple)
        "value": p.get("numero_dossier", p.get("id", "")),
    }]
    if p.get("cnam"):
        identifiers.append({"system": "urn:medisuite:cnam", "value": p["cnam"]})
    return {
        "resourceType": "Patient",
        "id": str(p.get("id", "")),
        "identifier": identifiers,
        "active": True,
        "name": names,
        "gender": {"M": "male", "F": "female"}.get(p.get("sexe", ""), "unknown"),
        "birthDate": p.get("date_naissance"),
        "address": [{"city": p.get("ville", "Abidjan"), "country": "CI"}],
        "telecom": [{"system": "phone", "value": p.get("telephone", "")}],
    }


def observation_to_fhir(o: dict, patient_id: str) -> dict:
    """Résultat de laboratoire / signe vital → FHIR R4 Observation (LOINC)."""
    value_block: dict[str, Any]
    if isinstance(o.get("valeur"), str):
        value_block = {"valueString": o["valeur"]}
    else:
        value_block = {"valueQuantity": {
            "value": o.get("valeur"), "unit": o.get("unite", ""),
            "system": "http://unitsofmeasure.org", "code": o.get("unite", "")}}
    return {
        "resourceType": "Observation",
        "id": str(o.get("id", "")),
        "status": "final" if o.get("valide") else "preliminary",
        "code": {"coding": [{
            "system": "http://loinc.org",
            "code": o.get("loinc", ""), "display": o.get("analyse", "")}]},
        "subject": _ref("Patient", patient_id),
        "effectiveDateTime": o.get("date_resultat"),
        **value_block,
        "referenceRange": ([{"low": {"value": o["ref_basse"]},
                             "high": {"value": o["ref_haute"]}}]
                           if o.get("ref_basse") is not None else []),
    }


def condition_to_fhir(c: dict, patient_id: str) -> dict:
    """Diagnostic / problème de santé → FHIR R4 Condition (CIM-10)."""
    return {
        "resourceType": "Condition",
        "id": str(c.get("id", "")),
        "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                        "code": c.get("statut", "active")}]},
        "code": {"coding": [{
            "system": "http://hl7.org/fhir/sid/icd-10",
            "code": c.get("cim10", ""), "display": c.get("libelle", "")}]},
        "subject": _ref("Patient", patient_id),
        "recordedDate": c.get("date_diagnostic"),
        "severity": {"text": c.get("severite", "")} if c.get("severite") else None,
    }


def encounter_to_fhir(e: dict, patient_id: str) -> dict:
    """Consultation / hospitalisation → FHIR R4 Encounter."""
    return {
        "resourceType": "Encounter",
        "id": str(e.get("id", "")),
        "status": e.get("statut", "finished"),
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                   "code": e.get("classe", "AMB")},
        "subject": _ref("Patient", patient_id),
        "period": {"start": e.get("debut"), "end": e.get("fin")},
        "reasonCode": [{"text": e.get("motif", "")}] if e.get("motif") else [],
    }


def bundle(entries: list[dict]) -> dict:
    """FHIR R4 Bundle de type searchset."""
    return {"resourceType": "Bundle", "type": "searchset",
            "total": len(entries),
            "entry": [{"resource": r} for r in entries]}
