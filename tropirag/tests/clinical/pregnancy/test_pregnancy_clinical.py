"""Scénarios cliniques V1.1 — grossesse (paludisme gestationnel, dengue gravidique).

Vérifie : urgence materno-fœtale, contre-indications (primaquine, SP 1er trimestre,
AINS 3e trimestre, doxycycline), artésunate préféré à la quinine, souffrance fœtale.
"""
import pytest

from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestPaludismeGestationnel:
    """Fièvre + grossesse + zone palu = urgence materno-fœtale."""

    def test_urgence_materno_foetale(self, days_ago):
        r = process_case({
            "patient": {"age_years": 24, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 22},
            "free_text": "fièvre 38,9, céphalées, frissons",
            "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                     "departure": days_ago(10)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "malaria_pregnancy_urgent" in codes_
        assert r.urgency in ("emergency", "immediate")

    def test_tdr_immediat(self, days_ago):
        r = process_case({
            "patient": {"age_years": 28, "sex": "female", "pregnant": "pregnant"},
            "free_text": "fièvre",
            "travel": {"segments": [{"country": "BF", "departure": days_ago(14)}]},
        })
        tests = {t["test"] for t in r.required_tests}
        assert "rdt_malaria" in tests

    def test_anemie_grossesse(self, days_ago):
        r = process_case({
            "patient": {"age_years": 31, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 26},
            "free_text": "fièvre, fatigue intense, pâleur",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(9)}]},
            "lab_results": [{"test": "cbc", "component": "hb", "numeric": 7.1, "unit": "g/dL"}],
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "severe_anemia_pregnancy" in codes_


class TestContreIndicationsGrossesse:
    """Le garde-fou médicamenteux gravidique."""

    def test_primaquine_interdite(self, days_ago):
        r = process_case({
            "patient": {"age_years": 22, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 18},
            "free_text": "fièvre, frissons",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(5)}]},
        })
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "primaquine" in forbidden

    def test_doxy_interdite(self, days_ago):
        r = process_case({
            "patient": {"age_years": 25, "sex": "female", "pregnant": "pregnant"},
            "free_text": "fièvre depuis 6 jours, douleurs abdominales",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(20)}]},
        })
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "doxycycline" in forbidden

    def test_sp_interdite_1er_trimestre(self, days_ago):
        r = process_case({
            "patient": {"age_years": 19, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 9},
            "free_text": "fièvre modérée",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(3)}]},
        })
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "sulfadoxine_pyrimethamine" in forbidden

    def test_ains_interdits_3e_trimestre(self, days_ago):
        r = process_case({
            "patient": {"age_years": 33, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 34},
            "free_text": "fièvre 39, céphalées, douleurs derrière les yeux",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(6)}]},
        })
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "ibuprofen" in forbidden
        allowed = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "paracetamol" in allowed or "folic_acid" in allowed


class TestPaludismeSevereGravidique:
    """Formes sévères : artésunate IV, hypoglycémie, transfert médicalisé."""

    def test_artesunate_prefere_quinine(self, days_ago):
        r = process_case({
            "patient": {"age_years": 27, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 30},
            "free_text": "fièvre 40, prostration, essoufflement",
            "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                     "departure": days_ago(7)}]},
            "vitals": {"temperature_c": 40.1},
        })
        allowed = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "artesunate_iv" in allowed
        assert r.urgency == "immediate"

    def test_hypoglycemie_surveillance(self, days_ago):
        r = process_case({
            "patient": {"age_years": 26, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 20},
            "free_text": "fièvre, sueurs, tremblements, confusion légère",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(4)}]},
            "lab_results": [{"test": "glucose", "numeric": 2.8, "unit": "mmol/L"}],
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "hypoglycemia_pregnancy" in codes_


class TestSouffranceFoetaleEtDengue:
    """Souffrance fœtale et dengue gravidique."""

    def test_mouvements_actifs_diminues(self, days_ago):
        r = process_case({
            "patient": {"age_years": 29, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 36},
            "free_text": "fièvre depuis hier et le bébé bouge moins depuis ce matin",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(15)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "fetal_distress_risk" in codes_
        assert r.severity == "critical"

    def test_dengue_gravidique_surveillance(self, days_ago):
        r = process_case({
            "patient": {"age_years": 23, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 28},
            "free_text": "fièvre 39, douleur derrière les yeux, myalgies, éruption",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                     "departure": days_ago(5)}]},
        })
        assert r.escalations, "dengue + grossesse sans escalade"
        assert validate_response(r) == []

    def test_hemorragie_dengue_enceinte(self, days_ago):
        r = process_case({
            "patient": {"age_years": 30, "sex": "female", "pregnant": "pregnant",
                        "gestational_age_weeks": 25},
            "free_text": "fièvre, saignements des gencives et pétéchies",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(4)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "dengue_pregnancy_hemorrhagic" in codes_


class TestGrossesseNonRegression:
    """Sans grossesse → pas de contraintes gravidiques."""

    def test_homme_fievre_pas_de_ci_grossesse(self, days_ago):
        r = process_case({
            "patient": {"age_years": 40, "sex": "male"},
            "free_text": "fièvre, frissons",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(6)}]},
        })
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "primaquine" not in forbidden
        assert "sulfadoxine_pyrimethamine" not in forbidden
