"""eCRF FHIR de l'investigation MEDISUITE-CI-01 (R5/R6). v0.7.

Implémente la maquette CRF (annexe A1 du protocole TD-10) et le §8 eCRF :
- identification pseudonymisée (code étude + site + numéro séquentiel) ;
- formulaires F01-F06 (inclusion, baseline, décisions, suivi 30 j,
  adjudication, déviations) avec contrôles de cohérence à la saisie ;
- dérivations SAP (éligibilité §4.2/§4.3, délai de priorisation P3) ;
- mapping FHIR R4 vers les profils nationaux IOP (ADR-0024) pour ingestion
  par le hub HAPI du site ;
- idempotence de la synchronisation offline (clé dérivée du payload
  canonique — le même formulaire rejoué deux fois ne crée rien).

Zéro dépendance : fonctions pures testables sans serveur ni base.
La persistance, le RBAC et l'audit chaîné vivent dans ecrf-service.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

# ── Constantes d'étude (protocole TD-10 §0) ──────────────────────────────────

STUDY_CODE = "MEDISUITE-CI-01"
STUDY_VERSION = "1.0.0-draft"
STUDY_SYSTEM = f"urn:medisuite:study:{STUDY_CODE}"

SITES: dict[str, str] = {
    "COC": "CHU de Cocody (coordinateur)",
    "TRI": "CHU de Treichville",
    "YOP": "CHU de Yopougon",
    "BOU": "CHU de Bouaké (extension DSMB, §4.1)",
}

SCENARIOS: dict[str, str] = {
    "S1": "Code AVC (LKW, NIHSS, ASPECTS, fenêtres rtPA)",
    "S2": "BI-RADS (catégorisation mammographique)",
    "S3": "Triage ISS/ESI (priorisation urgences)",
    "S4": "Validation laboratoire (valeurs critiques, delta check)",
    "S5": "Fusion multimodale (modalités manquantes ADR-0018)",
}

_CONSENT_OK = ("ecrit", "differe_urgence")
_EI_GRAVITE = ("aucun", "EI", "SAE")
_ADHESION = ("acceptee", "partielle", "refusee")
_STATUT_30J = ("vivant", "deces", "perdu_de_vue")

_SUBJECT_RE = re.compile(
    r"^CI01-(?P<site>" + "|".join(SITES) + r")-\d{5}$")

_ISO_DT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?$")

# URL des artefacts de profils (ADR-0024) attachés aux ressources générées.
PROFILE_PATIENT = "http://medisuite.ci/fhir/StructureDefinition/Patient-CI-IOP"
PROFILE_OBSERVATION = ("http://medisuite.ci/fhir/StructureDefinition/"
                       "Observation-CI-IOP")
CODE_SYSTEM = f"http://medisuite.ci/fhir/CodeSystem/{STUDY_CODE}"

# ── Définition des formulaires (annexe A1) ───────────────────────────────────
# Chaque champ : type (str/enum/int/float/bool/datetime/text), required,
# choices, min/max, libellé. La définition EST la spécification saisie côté
# web-portal (source unique) et validée côté service (défense en profondeur).

FORMS: dict[str, dict[str, Any]] = {
    "F01-INCLUSION": {
        "titre": "Inclusion et consentement (§4.2)",
        "role": "investigateur",
        "fields": [
            {"id": "date_passage", "type": "date", "required": True},
            {"id": "scenario", "type": "enum", "required": True,
             "choices": list(SCENARIOS)},
            {"id": "consentement", "type": "enum", "required": True,
             "choices": list(_CONSENT_OK) + ["refuse"],
             "libelle": "écrit / différé urgence (ISO 14155 §6.7) / refus"},
            {"id": "age", "type": "int", "required": True, "min": 18,
             "max": 120, "libelle": "≥ 18 ans"},
            {"id": "grossesse", "type": "bool", "required": False,
             "libelle": "grossesse (exclusion si scénario irradiant S2)"},
            {"id": "perte_modalites", "type": "int", "required": True,
             "min": 0, "max": 10,
             "libelle": "modalités primaires manquantes (§4.3 : > 2 → non évaluable)"},
            {"id": "panne_site_24h", "type": "bool", "required": False},
            {"id": "doublon_14j", "type": "bool", "required": False},
        ],
    },
    "F02-BASELINE": {
        "titre": "Caractéristiques de base (pseudonymisées)",
        "role": "investigateur",
        "fields": [
            {"id": "sexe", "type": "enum", "required": True,
             "choices": ["M", "F"]},
            {"id": "tranche_age", "type": "enum", "required": True,
             "choices": ["18-39", "40-59", "60-74", "75+"]},
            {"id": "provenance", "type": "enum", "required": True,
             "choices": ["urgences", "imagerie", "laboratoire"]},
            {"id": "comorbidites", "type": "text", "required": False,
             "max": 400, "libelle": "liste libre (HTA, diabète…)"},
        ],
    },
    "F03-DECISION": {
        "titre": "Décisions intra-patient appariées (§4.1) et sorties dispositif",
        "role": "investigateur",
        "fields": [
            {"id": "decision_standard", "type": "text", "required": True,
             "min": 3, "max": 1000, "libelle": "décision pratique standard AVANT dispositif"},
            {"id": "decision_finale", "type": "text", "required": True,
             "min": 3, "max": 1000, "libelle": "décision finale APRÈS consultation dispositif"},
            {"id": "adhesion", "type": "enum", "required": True,
             "choices": list(_ADHESION)},
            {"id": "dispositif_consulte", "type": "bool", "required": True},
            {"id": "score_dispositif", "type": "float", "required": False,
             "min": 0.0, "max": 1.0, "libelle": "score/confiance de la sortie IA"},
            {"id": "importance_modalites", "type": "text", "required": False,
             "max": 2000, "libelle": "JSON importance des modalités (ADR-0015)"},
            {"id": "horodatage_triage", "type": "datetime", "required": True},
            {"id": "horodatage_orientation", "type": "datetime", "required": True},
        ],
    },
    "F04-SUIVI30J": {
        "titre": "Suivi à 30 jours et événements indésirables (§6)",
        "role": "investigateur",
        "fields": [
            {"id": "statut_30j", "type": "enum", "required": True,
             "choices": list(_STATUT_30J)},
            {"id": "ei_lie_dispositif", "type": "bool", "required": True},
            {"id": "ei_gravite", "type": "enum", "required": True,
             "choices": list(_EI_GRAVITE)},
            {"id": "ei_description", "type": "text", "required": False,
             "max": 2000},
            {"id": "hospitalisation", "type": "bool", "required": False},
        ],
    },
    "F05-ADJUDICATION": {
        "titre": "Référence adjudiquée (§3.3, annexe A3) — comité aveugle",
        "role": "adjudicateur",
        "fields": [
            {"id": "verdict_standard", "type": "text", "required": True,
             "min": 1, "max": 1000},
            {"id": "verdict_final", "type": "text", "required": True,
             "min": 1, "max": 1000},
            {"id": "certitude", "type": "int", "required": True, "min": 1,
             "max": 5, "libelle": "échelle de certitude du comité"},
            {"id": "tierce_requis", "type": "bool", "required": True,
             "libelle": "désaccord 1ers juges → tierce arbitre"},
            {"id": "verdict_tierce", "type": "text", "required": False,
             "max": 1000},
            {"id": "dossier_complet", "type": "bool", "required": True},
        ],
    },
    "F06-DEVIATION": {
        "titre": "Déviation protocole (§6, registre)",
        "role": "investigateur",
        "fields": [
            {"id": "type", "type": "enum", "required": True,
             "choices": ["retard_saisie", "panne", "donnee_manquante",
                          "consentement_tardif", "autre"]},
            {"id": "description", "type": "text", "required": True,
             "min": 3, "max": 2000},
            {"id": "impact_evaluabilite", "type": "bool", "required": True,
             "libelle": "déviation majeure → sortie PP (§7.1)"},
        ],
    },
}

FORM_ROLES = {fid: spec["role"] for fid, spec in FORMS.items()}


class EcrfValidationError(ValueError):
    """Formulaire non conforme (contrôles de cohérence à la saisie, §8)."""


# ── Identification pseudonymisée (§6 confidentialité) ────────────────────────

def is_valid_subject_code(code: str) -> bool:
    """Code étude : CI01-<SITE>-NNNNN (pseudonyme ; jamais le nom)."""
    return bool(_SUBJECT_RE.match((code or "").strip().upper()))


def new_subject_code(site: str, sequence: int) -> str:
    """Construit le code d'un sujet pour un site donné (1-99999)."""
    site = (site or "").strip().upper()
    if site not in SITES:
        raise EcrfValidationError(f"site inconnu : '{site}' "
                                  f"(attendus : {', '.join(SITES)})")
    if not 1 <= int(sequence) <= 99999:
        raise EcrfValidationError("séquence hors bornes (1-99999)")
    return f"CI01-{site}-{sequence:05d}"


# ── Contrôles de cohérence à la saisie (§8 eCRF) ────────────────────────────

def _check_field(field: dict, value: Any) -> str | None:
    """Retourne un message d'erreur ou None si le champ est valide."""
    fid, ftype = field["id"], field["type"]
    if value is None or value == "":
        return None if not field.get("required") else f"{fid} : requis"
    if ftype == "enum":
        if value not in field["choices"]:
            return f"{fid} : valeur '{value}' hors liste autorisée"
    elif ftype == "bool":
        if not isinstance(value, bool):
            return f"{fid} : attendu booléen"
    elif ftype == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            return f"{fid} : attendu entier"
        if "min" in field and value < field["min"]:
            return f"{fid} : {value} < minimum {field['min']}"
        if "max" in field and value > field["max"]:
            return f"{fid} : {value} > maximum {field['max']}"
    elif ftype == "float":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return f"{fid} : attendu numérique"
        if "min" in field and value < field["min"]:
            return f"{fid} : {value} < minimum {field['min']}"
        if "max" in field and value > field["max"]:
            return f"{fid} : {value} > maximum {field['max']}"
    elif ftype == "datetime":
        if not isinstance(value, str) or not _ISO_DT_RE.match(value):
            return f"{fid} : format attendu AAAA-MM-JJThh:mm"
    elif ftype == "date":
        if not isinstance(value, str):
            return f"{fid} : attendu chaîne AAAA-MM-JJ"
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return f"{fid} : date invalide '{value}'"
    elif ftype in ("str", "text"):
        if not isinstance(value, str):
            return f"{fid} : attendu texte"
        if len(value) < field.get("min", 0):
            return f"{fid} : moins de {field['min']} caractères"
        if len(value) > field.get("max", 100000):
            return f"{fid} : plus de {field['max']} caractères"
    return None


def validate_entry(form_id: str, payload: dict) -> list[str]:
    """Valide un formulaire contre sa définition ; retourne les erreurs ([]=OK).

    Contrôles de cohérence (§8) : champs requis, listes fermées, bornes,
    formats horodatés, cohérence temporelle et conditionnelle.
    """
    spec = FORMS.get(form_id)
    if spec is None:
        return [f"form_id inconnu : '{form_id}' "
                f"(formulaires : {', '.join(FORMS)})"]
    if not isinstance(payload, dict):
        return ["payload : attendu objet JSON"]
    errors: list[str] = []
    for field in spec["fields"]:
        err = _check_field(field, payload.get(field["id"]))
        if err:
            errors.append(err)
    # Cohérences transversales
    if form_id == "F03-DECISION":
        tri = payload.get("horodatage_triage")
        ori = payload.get("horodatage_orientation")
        if isinstance(tri, str) and isinstance(ori, str) and ori < tri:
            errors.append("horodatage_orientation : antérieur au triage")
    if form_id == "F05-ADJUDICATION":
        if payload.get("tierce_requis") is True and not payload.get("verdict_tierce"):
            errors.append("verdict_tierce : requis quand tierce_requis = true")
    if form_id == "F04-SUIVI30J":
        if payload.get("ei_gravite") in ("EI", "SAE") and not payload.get("ei_description"):
            errors.append("ei_description : requise pour un EI/SAE (§6)")
    return errors


# ── Dérivations SAP (annexe A5) ──────────────────────────────────────────────

def derive_eligibility(f01: dict) -> tuple[str, str]:
    """Éligibilité dérivée du F01 (§4.2 inclusion, §4.3 non-éligibilité).

    Retourne (statut, motif) parmi :
    - ("inclus", "consentement_ecrit"|"consentement_differe_urgence")
    - ("refuse", "consentement_refuse")
    - ("non_eligible", motif §4.2)
    - ("non_evaluable", motif §4.3 — inclus mais retiré de l'évaluable,
      conservé en ITT)
    """
    if f01.get("consentement") == "refuse":
        return "refuse", "consentement refusé (§4.2)"
    if f01.get("consentement") not in _CONSENT_OK:
        return "non_eligible", "consentement absent ou invalide"
    if f01.get("scenario") == "S2" and f01.get("grossesse") is True:
        return "non_eligible", "grossesse avec scénario irradiant (§4.2)"
    if f01.get("perte_modalites", 0) > 2:
        return "non_evaluable", ("perte > 2 modalités primaires (§4.3) "
                                 "— conservé en ITT")
    if f01.get("doublon_14j") is True:
        return "non_evaluable", "doublon patient dans 14 j (§4.3)"
    motif_consent = ("consentement_differe_urgence"
                     if f01.get("consentement") == "differe_urgence"
                     else "consentement_ecrit")
    return "inclus", motif_consent


def derive_delai_minutes(f03: dict) -> float | None:
    """Délai triage → orientation en minutes (endpoint P3, §3.2)."""
    tri, ori = f03.get("horodatage_triage"), f03.get("horodatage_orientation")
    if not isinstance(tri, str) or not isinstance(ori, str):
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M"):
        try:
            dt = (datetime.strptime(tri, fmt), datetime.strptime(ori, fmt))
            return round((dt[1] - dt[0]).total_seconds() / 60.0, 2)
        except ValueError:
            continue
    return None


def is_sae(f04: dict) -> bool:
    """Vrai si l'entrée F04 rapporte un SAE lié au dispositif (§6)."""
    return f04.get("ei_gravite") == "SAE" and f04.get("ei_lie_dispositif") is True


# ── Idempotence offline (synchronisation R6) ────────────────────────────────

def canonical_payload(payload: dict) -> str:
    """Sérialisation canonique (clés triées, séparateurs denses)."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def dedup_key(subject_code: str, form_id: str, payload: dict) -> str:
    """Clé d'idempotence : SHA-256(étude|sujet|formulaire|payload canonique).

    Une saisie offline rejouée (même contenu) produit la même clé → le
    serveur répond « duplicate » au lieu de créer une seconde entrée.
    """
    base = f"{STUDY_CODE}|{subject_code}|{form_id}|{canonical_payload(payload)}"
    return hashlib.sha256(base.encode()).hexdigest()


# ── Mapping FHIR R4 → profils IOP (ADR-0024, §8 eCRF) ───────────────────────

def entry_to_fhir(subject_code: str, form_id: str, payload: dict,
                  site: str, entry_id: str = "") -> dict:
    """Bundle FHIR R4 d'une entrée eCRF pour ingestion par le hub HAPI.

    - Patient pseudonyme (identifiant = code étude, profil Patient-CI-IOP) ;
    - une Observation-CI-IOP par champ renseigné (CodeSystem étude) ;
    - statuts d'éligibilité en Observation dérivée (statut-final).
    Aucune donnée identifiante ne quitte le site (§6 : pseudonymisation
    à l'ingestion).
    """
    spec = FORMS.get(form_id)
    if spec is None:
        raise EcrfValidationError(f"form_id inconnu : '{form_id}'")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    patient_id = subject_code.replace("CI01-", "SUBJ-").lower()
    bundle: dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [],
    }
    patient = {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {"profile": [PROFILE_PATIENT]},
        "identifier": [{"system": STUDY_SYSTEM, "value": subject_code,
                        "use": "official"}],
    }
    bundle["entry"].append({"resource": patient,
                            "request": {"method": "PUT",
                                        "url": f"Patient/{patient_id}"}})
    for field in spec["fields"]:
        value = payload.get(field["id"])
        if value is None or value == "":
            continue
        form_prefix = form_id.split("-")[0]  # "F01-INCLUSION" → "F01"
        obs_id = f"{patient_id}-{form_prefix.lower()}-{field['id']}"
        obs: dict[str, Any] = {
            "resourceType": "Observation",
            "id": obs_id,
            "meta": {"profile": [PROFILE_OBSERVATION]},
            "status": "final",
            "code": {"coding": [{
                "system": CODE_SYSTEM,
                "code": f"{form_prefix}.{field['id']}",
                "display": field.get("libelle", field["id"]),
            }]},
            "subject": {"reference": f"Patient/{patient_id}",
                        "display": subject_code},
            "effectiveDateTime": now,
            "extension": [{
                "url": f"{CODE_SYSTEM}/site",
                "valueString": site,
            }],
        }
        if isinstance(value, bool):
            obs["valueBoolean"] = value
        elif isinstance(value, (int, float)):
            obs["valueQuantity"] = {"value": value}
        else:
            obs["valueString"] = str(value)
        bundle["entry"].append({"resource": obs,
                                "request": {"method": "PUT",
                                            "url": f"Observation/{obs_id}"}})
    # Dérivations utiles à l'analyse, portées dans le bundle
    if form_id == "F01-INCLUSION":
        statut, motif = derive_eligibility(payload)
        bundle["entry"].append({"resource": {
            "resourceType": "Observation",
            "id": f"{patient_id}-f01-eligibilite",
            "meta": {"profile": [PROFILE_OBSERVATION]},
            "status": "final",
            "code": {"coding": [{"system": CODE_SYSTEM,
                                 "code": "F01.eligibilite",
                                 "display": "statut d'éligibilité dérivé"}]},
            "subject": {"reference": f"Patient/{patient_id}",
                        "display": subject_code},
            "valueString": f"{statut}:{motif}",
        }, "request": {"method": "PUT",
                       "url": f"Observation/{patient_id}-f01-eligibilite"}})
    if entry_id:
        bundle.setdefault("extension", []).append({
            "url": f"{CODE_SYSTEM}/ecrf-entry", "valueString": entry_id})
    return bundle


def forms_catalog() -> list[dict[str, Any]]:
    """Catalogue servi au web-portal (GET /api/v1/ecrf/forms)."""
    return [{"id": fid, "titre": spec["titre"], "role": spec["role"],
             "scenario_hint": "S1-S5" if fid != "F05-ADJUDICATION" else "S1-S5",
             "fields": [dict(f) for f in spec["fields"]]}
            for fid, spec in FORMS.items()]
