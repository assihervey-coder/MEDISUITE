"""Leptospirose — scénarios cliniques V1.3.

Couverture : triade classique + eaux stagnantes (suspicion), maladie de Weil
(ictère + atteinte rénale → pénicilline G IV + AINS interdits), hémorragie
alvéolaire, myocardite, notification autorité, bilan diagnostique, et contrôle
négatif (leptospirose non suspectée sans exposition).
"""
import pytest

from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestSuspicionLeptospirose:
    def test_triade_eaux_stagnantes(self, days_ago):
        r = process_case({
            "patient": {"age_years": 30},
            "free_text": "fièvre depuis 4 jours, courbatures très intenses, yeux rouges",
            "travel": {"segments": [{"country": "CI", "stagnant_water": True,
                                      "rural_stay": True, "departure": days_ago(21)}]},
            "vitals": {"temperature_c": 38.8},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "leptospirosis" in diseases, "leptospirose attendue dans le différentiel"
        tests = {t["test"] for t in r.required_tests}
        assert "lepto_pcr" in tests and "lepto_serology" in tests
        # forme non sévère : doxycycline
        recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "doxycycline" in recos
        assert validate_response(r) == []

    def test_triade_sans_exposition_documentee(self):
        r = process_case({
            "patient": {"age_years": 45},
            "free_text": "fièvre, myalgies, conjonctives injectées",
            "vitals": {"temperature_c": 38.5},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "leptospirosis" in diseases, (
            "triade fièvre+myalgies+injection conjonctivale → suspicion même sans exposition")


class TestMaladieDeWeil:
    def test_weil_ictiere_oligurie(self, days_ago):
        r = process_case({
            "patient": {"age_years": 34},
            "free_text": "fièvre depuis 5 jours, myalgies, jaunisse, urine très peu",
            "travel": {"segments": [{"country": "CI", "stagnant_water": True,
                                      "departure": days_ago(20)}]},
            "vitals": {"temperature_c": 39.0},
            "lab_results": [{"test": "creatinine", "value": 2.4}],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "leptospirosis_weil_disease" in codes, "Weil attendu (ictère + rénal)"
        assert r.urgency == "immediate" and r.severity == "critical"
        # pénicilline G IV recommandée ; AINS interdits
        recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        forb = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "benzylpenicillin" in recos
        assert {"ibuprofen", "aspirin", "diclofenac"} <= forb
        # escalade + notification
        assert any(e["level"] == "refer_hospital" for e in r.escalations)
        assert any("leptospirose" in str(n).lower() for n in r.notifications)
        assert validate_response(r) == []

    def test_hemorragie_alveolaire(self, days_ago):
        r = process_case({
            "patient": {"age_years": 28},
            "free_text": "fièvre, crachats sanglants, myalgies intenses",
            "travel": {"segments": [{"country": "CI", "stagnant_water": True,
                                      "departure": days_ago(18)}]},
            "vitals": {"temperature_c": 39.2},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "leptospirosis_pulmonary_hemorrhage" in codes
        assert r.urgency == "immediate"
        assert any(e["level"] == "emergency_transfer" for e in r.escalations)


class TestMyocarditeEtNotification:
    def test_myocardite(self, days_ago):
        r = process_case({
            "patient": {"age_years": 41},
            "free_text": "fièvre depuis 6 jours, douleur dans la poitrine, myalgies",
            "travel": {"segments": [{"country": "CI", "stagnant_water": True,
                                      "departure": days_ago(25)}]},
            "vitals": {"temperature_c": 38.6},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "leptospirosis_myocarditis" in codes
        assert r.severity == "severe"


class TestControlesNegatifs:
    def test_pas_de_lepto_sans_contexte(self):
        r = process_case({
            "patient": {"age_years": 30},
            "free_text": "fièvre et toux depuis 2 jours",
            "vitals": {"temperature_c": 38.1},
        })
        codes = [f["code"] for f in r.red_flags]
        assert not any(c.startswith("leptospirosis_") for c in codes), (
            "aucun drapeau leptospirose sans exposition ni triade")

    def test_differential_fievre_ictérique_inclut_lepto(self, days_ago):
        """Fièvre ictérique en zone humide : lepto ET paludisme sévère co-suspectés."""
        r = process_case({
            "patient": {"age_years": 34},
            "free_text": "fièvre ictérique depuis 4 jours",
            "travel": {"segments": [{"country": "CI", "stagnant_water": True,
                                      "departure": days_ago(20)}]},
            "vitals": {"temperature_c": 39.1},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "leptospirosis" in diseases
        assert "malaria" in diseases, "le paludisme sévère reste must-not-miss"
