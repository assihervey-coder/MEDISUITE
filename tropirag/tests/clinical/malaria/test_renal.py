"""Paludisme rénal — AKI et épuration extrarénale, scénarios V1.2.

Couverture : créatinine en mg/dL et µmol/L (conversion déterministe),
critère OMS de paludisme sévère, indications d'EER (hyperkaliémie, acidose),
escalade vers structure avec dialyse, néphroprotection médicamenteuse.
"""
import pytest

from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestAKIPaludisme:
    def test_creatinine_mgdl_seuil_oms(self, days_ago):
        r = process_case({
            "patient": {"age_years": 37},
            "free_text": "fièvre depuis 4 jours, frissons, urines foncées",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(12)}]},
            "lab_results": [{"test": "creatinine", "numeric": 3.4, "unit": "mg/dL"}],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "malaria_acute_kidney_injury" in codes
        assert r.urgency in ("emergency", "immediate")
        assert validate_response(r) == []

    def test_creatinine_umoll_conversion_automatique(self, days_ago):
        """300 µmol/L (terrain ivoirien) → 3,39 mg/dL : le seuil OMS s'applique."""
        r = process_case({
            "patient": {"age_years": 40},
            "free_text": "fièvre depuis 5 jours, vomissements",
            "travel": {"segments": [{"country": "BF", "departure": days_ago(15)}]},
            "lab_results": [{"test": "creatinine", "numeric": 300, "unit": "µmol/L"}],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "malaria_acute_kidney_injury" in codes

    def test_creatinine_intermediaire_avec_oligurie(self, days_ago):
        r = process_case({
            "patient": {"age_years": 52},
            "free_text": "fièvre depuis 5 jours, frissons",
            "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                      "departure": days_ago(10)}]},
            "symptom_codes": ["oliguria"],
            "lab_results": [{"test": "creatinine", "numeric": 1.9, "unit": "mg/dL"}],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "malaria_acute_kidney_injury" in codes
        assert "malaria_oliguric_aki" in codes


class TestIndicationsEER:
    def test_hyperkaliemie_avec_aki(self, days_ago):
        r = process_case({
            "patient": {"age_years": 34},
            "free_text": "fièvre depuis 4 jours, prostration",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(9)}]},
            "lab_results": [
                {"test": "creatinine", "numeric": 4.1, "unit": "mg/dL"},
                {"test": "potassium", "numeric": 6.9, "unit": "mmol/L"},
            ],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "malaria_acute_kidney_injury" in codes
        assert "hyperkalemia_emergency" in codes
        assert "malaria_rrt_indication" in codes
        # escalade vers structure avec dialyse
        assert any("puration" in e["message"] or "dialyse" in e["message"].lower()
                   for e in r.escalations)

    def test_acidose_severe_avec_aki(self, days_ago):
        r = process_case({
            "patient": {"age_years": 48},
            "free_text": "fièvre depuis 6 jours, confusion",
            "travel": {"segments": [{"country": "ML", "departure": days_ago(13)}]},
            "lab_results": [
                {"test": "creatinine", "numeric": 3.8, "unit": "mg/dL"},
                {"test": "blood_gas", "component": "ph", "numeric": 7.12, "unit": "pH"},
            ],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "malaria_rrt_indication" in codes

    def test_surveillance_biologique_exigee(self, days_ago):
        r = process_case({
            "patient": {"age_years": 41},
            "free_text": "fièvre depuis 5 jours",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(11)}]},
            "lab_results": [{"test": "creatinine", "numeric": 3.2, "unit": "mg/dL"}],
        })
        tests = {t["test"] for t in r.required_tests}
        assert {"creatinine", "urea", "potassium", "blood_gas"} <= tests


class TestNephroprotection:
    def test_ains_interdits_en_aki(self, days_ago):
        r = process_case({
            "patient": {"age_years": 36},
            "free_text": "fièvre depuis 4 jours",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(8)}]},
            "lab_results": [{"test": "creatinine", "numeric": 3.5, "unit": "mg/dL"}],
        })
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "ibuprofen" in forbidden
