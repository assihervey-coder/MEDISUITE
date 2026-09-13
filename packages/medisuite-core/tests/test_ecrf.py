"""Tests eCRF MEDISUITE-CI-01 (v0.7) : domaines purs du protocole R5/R6."""
from medisuite_core import ecrf


# ── Identification pseudonymisée ─────────────────────────────────────────────

def test_subject_code_valide():
    assert ecrf.is_valid_subject_code("CI01-COC-00042")
    assert ecrf.is_valid_subject_code("ci01-tri-00777")
    assert ecrf.new_subject_code("YOP", 1) == "CI01-YOP-00001"
    assert ecrf.new_subject_code("BOU", 99999) == "CI01-BOU-99999"


def test_subject_code_invalide():
    assert not ecrf.is_valid_subject_code("CI01-XXX-00001")     # site inconnu
    assert not ecrf.is_valid_subject_code("CI01-COC-123")       # séquence courte
    assert not ecrf.is_valid_subject_code("PATIENT-1")          # pas un code étude
    assert not ecrf.is_valid_subject_code("")


def test_new_subject_code_erreurs():
    for exc_call in (lambda: ecrf.new_subject_code("ZZZ", 10),
                     lambda: ecrf.new_subject_code("COC", 0),
                     lambda: ecrf.new_subject_code("COC", 100000)):
        try:
            exc_call()
            raised = False
        except ecrf.EcrfValidationError:
            raised = True
        assert raised


# ── Contrôles de cohérence à la saisie (§8) ──────────────────────────────────

F01_OK = {"date_passage": "2026-10-01", "scenario": "S1",
          "consentement": "ecrit", "age": 54, "perte_modalites": 0}


def test_forms_catalogue_complet():
    ids = set(ecrf.FORMS)
    assert {"F01-INCLUSION", "F02-BASELINE", "F03-DECISION",
            "F04-SUIVI30J", "F05-ADJUDICATION", "F06-DEVIATION"} == ids
    assert ecrf.FORM_ROLES["F05-ADJUDICATION"] == "adjudicateur"
    assert len(ecrf.forms_catalog()) == len(ecrf.FORMS)


def test_validation_f01_ok():
    assert ecrf.validate_entry("F01-INCLUSION", F01_OK) == []


def test_validation_champ_requis_manquant():
    errors = ecrf.validate_entry("F01-INCLUSION",
                                 {k: v for k, v in F01_OK.items()
                                  if k != "consentement"})
    assert any("consentement" in e for e in errors)


def test_validation_enum_hors_liste():
    errors = ecrf.validate_entry("F01-INCLUSION", F01_OK | {"scenario": "S9"})
    assert any("scenario" in e and "hors liste" in e for e in errors)


def test_validation_bornes():
    errors = ecrf.validate_entry("F01-INCLUSION", F01_OK | {"age": 16})
    assert any("age" in e and "minimum" in e for e in errors)
    errors = ecrf.validate_entry("F01-INCLUSION", F01_OK | {"perte_modalites": 5})
    # 5 > 2 : valide à la saisie (éligibilité traitée à part, §4.3)
    assert not any("perte_modalites" in e for e in errors)


def test_validation_form_id_inconnu():
    assert ecrf.validate_entry("F99-NOOP", {}) and \
        "inconnu" in ecrf.validate_entry("F99-NOOP", {})[0]


def test_validation_datetime_format():
    errors = ecrf.validate_entry(
        "F03-DECISION",
        {"decision_standard": "TDM", "decision_finale": "rtPA",
         "adhesion": "acceptee", "dispositif_consulte": True,
         "horodatage_triage": "01/09/2026", "horodatage_orientation": "2026-09-01T08:00"})
    assert any("horodatage_triage" in e for e in errors)


def test_validation_coherence_temporelle_f03():
    payload = {"decision_standard": "TDM", "decision_finale": "rtPA",
               "adhesion": "acceptee", "dispositif_consulte": True,
               "horodatage_triage": "2026-09-01T08:00",
               "horodatage_orientation": "2026-09-01T07:59"}
    errors = ecrf.validate_entry("F03-DECISION", payload)
    assert any("antérieur au triage" in e for e in errors)


def test_validation_f05_tierce_conditionnelle():
    base = {"verdict_standard": "AVC", "verdict_final": "AVC",
            "certitude": 4, "tierce_requis": True, "dossier_complet": True}
    errors = ecrf.validate_entry("F05-ADJUDICATION", base)
    assert any("verdict_tierce" in e for e in errors)
    assert ecrf.validate_entry("F05-ADJUDICATION",
                               base | {"verdict_tierce": "thrombectomie"}) == []


def test_validation_f04_sae_description_requise():
    base = {"statut_30j": "vivant", "ei_lie_dispositif": True,
            "ei_gravite": "SAE"}
    errors = ecrf.validate_entry("F04-SUIVI30J", base)
    assert any("ei_description" in e for e in errors)
    assert ecrf.validate_entry("F04-SUIVI30J",
                               base | {"ei_description": "convulsion"}) == []


# ── Dérivations SAP (annexe A5) ──────────────────────────────────────────────

def test_eligibilite_inclus():
    statut, motif = ecrf.derive_eligibility(F01_OK)
    assert (statut, motif) == ("inclus", "consentement_ecrit")


def test_eligibilite_consentement_differe_urgence():
    statut, _ = ecrf.derive_eligibility(F01_OK | {"consentement": "differe_urgence"})
    assert statut == "inclus"


def test_eligibilite_refus_et_grossesse():
    assert ecrf.derive_eligibility(F01_OK | {"consentement": "refuse"})[0] == "refuse"
    statut, motif = ecrf.derive_eligibility(
        F01_OK | {"scenario": "S2", "grossesse": True})
    assert statut == "non_eligible" and "grossesse" in motif


def test_eligibilite_non_evaluable_conserve_itt():
    statut, motif = ecrf.derive_eligibility(F01_OK | {"perte_modalites": 3})
    assert statut == "non_evaluable" and "ITT" in motif
    statut, _ = ecrf.derive_eligibility(F01_OK | {"doublon_14j": True})
    assert statut == "non_evaluable"


def test_delai_minutes_p3():
    f03 = {"horodatage_triage": "2026-09-01T08:00",
           "horodatage_orientation": "2026-09-01T08:42"}
    assert ecrf.derive_delai_minutes(f03) == 42.0
    assert ecrf.derive_delai_minutes({}) is None


def test_is_sae():
    assert ecrf.is_sae({"ei_gravite": "SAE", "ei_lie_dispositif": True})
    assert not ecrf.is_sae({"ei_gravite": "SAE", "ei_lie_dispositif": False})
    assert not ecrf.is_sae({"ei_gravite": "EI", "ei_lie_dispositif": True})


# ── Idempotence offline (synchronisation R6) ────────────────────────────────

def test_dedup_key_stable_et_distincte():
    k1 = ecrf.dedup_key("CI01-COC-00001", "F03-DECISION",
                        {"a": 1, "b": [1, 2]})
    # ordre des clés sans incidence (payload canonique)
    k2 = ecrf.dedup_key("CI01-COC-00001", "F03-DECISION",
                        {"b": [1, 2], "a": 1})
    assert k1 == k2 and len(k1) == 64
    assert k1 != ecrf.dedup_key("CI01-COC-00001", "F03-DECISION", {"a": 2})
    assert k1 != ecrf.dedup_key("CI01-COC-00002", "F03-DECISION", {"a": 1})


# ── Mapping FHIR IOP (ADR-0024) ──────────────────────────────────────────────

def test_fhir_bundle_structure():
    bundle = ecrf.entry_to_fhir("CI01-COC-00001", "F01-INCLUSION", F01_OK,
                                "COC", "entry-1")
    assert bundle["resourceType"] == "Bundle" and bundle["type"] == "transaction"
    patient = bundle["entry"][0]["resource"]
    assert patient["resourceType"] == "Patient"
    assert patient["identifier"][0]["value"] == "CI01-COC-00001"
    assert ecrf.PROFILE_PATIENT in patient["meta"]["profile"]
    observations = [e["resource"] for e in bundle["entry"]
                    if e["resource"]["resourceType"] == "Observation"]
    # 5 champs F01 renseignés (grossesse/panne/doublon absents) + éligibilité
    assert len(observations) == 6
    assert all(ecrf.PROFILE_OBSERVATION in o["meta"]["profile"]
               for o in observations)
    codes = {o["code"]["coding"][0]["code"] for o in observations}
    assert "F01.eligibilite" in codes and "F01.age" in codes


def test_fhir_types_par_nature():
    payload = F01_OK | {"grossesse": False}
    bundle = ecrf.entry_to_fhir("CI01-COC-00002", "F01-INCLUSION", payload,
                                "COC")
    obs = {e["resource"]["code"]["coding"][0]["code"]: e["resource"]
           for e in bundle["entry"]
           if e["resource"]["resourceType"] == "Observation"}
    assert obs["F01.age"]["valueQuantity"]["value"] == 54
    assert obs["F01.grossesse"]["valueBoolean"] is False
    assert obs["F01.scenario"]["valueString"] == "S1"


def test_fhir_form_inconnu_leve():
    try:
        ecrf.entry_to_fhir("CI01-COC-00001", "F99", {}, "COC")
        raised = False
    except ecrf.EcrfValidationError:
        raised = True
    assert raised
