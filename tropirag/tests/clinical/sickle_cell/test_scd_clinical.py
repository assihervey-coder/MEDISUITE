"""Scénarios cliniques V1.1 — drépanocytose.

Vérifie : fièvre SCD = urgence (asplénie), syndrome thoracique aigu,
AVC, séquestration splénique, paludisme SCD, ostéomyélite, escalade.
"""
import pytest

from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestSCDFievre:
    """Toute fièvre chez un drépanocytaire est une urgence."""

    def test_fievre_scd_urgence(self, days_ago):
        r = process_case({
            "patient": {"age_years": 9, "chronic_conditions": ["drépanocytose SS"]},
            "free_text": "fièvre depuis ce matin, corps chaud",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(30)}]},
            "vitals": {"temperature_c": 38.6},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "scd_febrile_emergency" in codes_
        assert r.urgency in ("emergency", "immediate")

    def test_triplet_biologique_obligatoire(self, days_ago):
        r = process_case({
            "patient": {"age_years": 12, "chronic_conditions": ["drépanocytose"]},
            "free_text": "fièvre",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(10)}]},
        })
        tests = {t["test"] for t in r.required_tests}
        assert {"cbc", "blood_culture", "rdt_malaria"} <= tests

    def test_escalation_hopital(self, days_ago):
        r = process_case({
            "patient": {"age_years": 15, "chronic_conditions": ["drépanocytose SC"]},
            "free_text": "fièvre 39 degrés",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(5)}]},
        })
        assert r.escalations, "fièvre SCD sans escalade"
        levels = {e["level"] for e in r.escalations}
        assert "refer_hospital" in levels

    def test_antibio_probabiliste_recommande(self, days_ago):
        r = process_case({
            "patient": {"age_years": 6, "chronic_conditions": ["drépanocytose"]},
            "free_text": "fièvre 39,1",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(2)}]},
        })
        allowed = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "ceftriaxone" in allowed


class TestSCDComplications:
    """Complications vitales : ACS, AVC, séquestration, anémie."""

    def test_syndrome_thoracique_aigu(self, days_ago):
        r = process_case({
            "patient": {"age_years": 17, "chronic_conditions": ["drépanocytose"]},
            "free_text": "fièvre, douleur thoracique, toux, essoufflement",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(3)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "scd_acute_chest_syndrome" in codes_
        assert r.urgency == "immediate"
        assert r.severity == "critical"

    def test_avc_deficit_focal(self, days_ago):
        r = process_case({
            "patient": {"age_years": 14, "chronic_conditions": ["drepanocytose"]},
            "free_text": "fièvre et faiblesse d'un côté du corps",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(8)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "scd_stroke" in codes_

    def test_sequestration_splenique(self, days_ago):
        r = process_case({
            "patient": {"age_years": 3, "chronic_conditions": ["drépanocytose SS"]},
            "free_text": "fièvre, très pâle, ventre dur avec rate grosse et douloureuse",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(12)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "scd_splenic_sequestration" in codes_

    def test_anemie_severe_transfusionnelle(self, days_ago):
        r = process_case({
            "patient": {"age_years": 10, "chronic_conditions": ["drépanocytose"]},
            "free_text": "fièvre et grande fatigue",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(6)}]},
            "lab_results": [{"test": "cbc", "component": "hb", "numeric": 5.4, "unit": "g/dL"}],
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "scd_severe_anemia" in codes_


class TestSCDPaludismeEtDifferenciel:
    """SCD + paludisme + ostéomyélite dans le différentiel."""

    def test_paludisme_aggrave_scd(self, days_ago):
        r = process_case({
            "patient": {"age_years": 8, "chronic_conditions": ["drépanocytose"]},
            "free_text": "fièvre élevée, frissons, vomissements",
            "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                     "departure": days_ago(9)}]},
        })
        diseases = [d["disease"] for d in r.differentials]
        assert "malaria" in diseases
        assert "invasive_bacterial_infection" in diseases

    def test_osteomyelite_douleur_localisee(self, days_ago):
        r = process_case({
            "patient": {"age_years": 13, "chronic_conditions": ["drépanocytose"]},
            "free_text": "fièvre et douleur osseuse au tibia droit",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(4)}]},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "osteomyelitis" in diseases

    def test_crise_vaso_occlusive_escalade(self, days_ago):
        r = process_case({
            "patient": {"age_years": 20, "chronic_conditions": ["drépanocytose"]},
            "free_text": "crise osseuse très douloureuse avec fièvre",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(1)}]},
        })
        assert r.escalations, "crise VOC sans escalade"
        assert validate_response(r) == []

    def test_acide_folique_au_differenciel(self, days_ago):
        r = process_case({
            "patient": {"age_years": 11, "chronic_conditions": ["drépanocytose"]},
            "free_text": "fièvre",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(2)}]},
        })
        allowed = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "folic_acid" in allowed


class TestSCDNonRegression:
    """Sans drépanocytose déclarée → pas de déclenchement SCD."""

    def test_fievre_simple_sans_scd(self, days_ago):
        r = process_case({
            "patient": {"age_years": 9},
            "free_text": "fièvre depuis 2 jours, céphalées",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(7)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "scd_febrile_emergency" not in codes_
