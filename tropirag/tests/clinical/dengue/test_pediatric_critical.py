"""Dengue pédiatrique — soins critiques et critères d'intubation, scénarios V1.2.

Couverture : choc décompensé, choc compensé (remplissage prudent), critères
d'intubation (conscience, détresse respiratoire, choc réfractaire), phase
critique et prévention de la surcharge iatrogène.
"""
import pytest

from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestChocDenguePediatrique:
    def test_choc_decompense(self, days_ago):
        r = process_case({
            "patient": {"age_years": 6},
            "free_text": "fièvre depuis 4 jours, céphalées, vomissements, prostration, somnolence",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(9)}]},
            "vitals": {"temperature_c": 38.5, "systolic_bp": 64, "capillary_refill_s": 4},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "dengue_peds_decompensated_shock" in codes
        # message clinique : bolus 20 mL/kg réévalué
        shock = next(f for f in r.red_flags if f["code"] == "dengue_peds_decompensated_shock")
        assert "20 mL/kg" in shock["message"]
        # transfert réa pédiatrique
        assert any(e["level"] == "emergency_transfer" for e in r.escalations)
        assert r.urgency in ("immediate",)
        assert validate_response(r) == []

    def test_choc_compense_remplissage_prudent(self, days_ago):
        r = process_case({
            "patient": {"age_years": 8},
            "free_text": "fièvre depuis 3 jours, céphalées, douleurs derrière les yeux, vomissements",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(7)}]},
            "vitals": {"temperature_c": 38.9, "systolic_bp": 98, "capillary_refill_s": 3.5},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "dengue_peds_compensated_shock" in codes
        # pas encore de choc décompensé
        assert "dengue_peds_decompensated_shock" not in codes


class TestCritèresIntubation:
    def test_intubation_trouble_conscience(self, days_ago):
        r = process_case({
            "patient": {"age_years": 5},
            "free_text": "fièvre, céphalées, vomissements, puis coma",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(8)}]},
            "vitals": {"temperature_c": 38.2, "systolic_bp": 76},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "dengue_peds_intubation_criteria" in codes
        crit = next(f for f in r.red_flags if f["code"] == "dengue_peds_intubation_criteria")
        # protocole : critères + ventilation protectrice
        assert "PROTECTRICE" in crit["message"]
        assert "volumes courants" in crit["message"]

    def test_intubation_detresse_respiratoire(self, days_ago):
        r = process_case({
            "patient": {"age_years": 7},
            "free_text": "fièvre, céphalées, myalgies, vomissements, dyspnée importante",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(9)}]},
            "vitals": {"temperature_c": 38.6, "spo2_pct": 89},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "dengue_peds_intubation_criteria" in codes

    def test_adulte_sans_critere_pediatrique(self, days_ago):
        """Le protocole pédiatrique ne s'applique pas à l'adulte."""
        r = process_case({
            "patient": {"age_years": 34},
            "free_text": "fièvre, céphalées, vomissements, prostration",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(9)}]},
            "vitals": {"temperature_c": 38.8, "systolic_bp": 72},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "dengue_peds_intubation_criteria" not in codes
        assert "dengue_peds_decompensated_shock" not in codes


class TestPhaseCritiqueEtSurcharge:
    def test_sans_choc_pas_de_remplissage_systematique(self, days_ago):
        r = process_case({
            "patient": {"age_years": 9},
            "free_text": "fièvre, céphalées, arthralgies, nausées",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(6)}]},
            "vitals": {"temperature_c": 38.4, "systolic_bp": 106, "capillary_refill_s": 2},
        })
        # pas de choc : règle de prudence sur la surcharge iatrogène active
        assert "den-peds-avoid-overload-006" in r.matched_rule_ids
        # monitorage de la phase critique actif
        assert "den-peds-monitoring-005" in r.matched_rule_ids
        # pas de remplissage déclenché
        codes = [f["code"] for f in r.red_flags]
        assert "dengue_peds_compensated_shock" not in codes

    def test_ains_toujours_interdits_en_dengue_enfant(self, days_ago):
        r = process_case({
            "patient": {"age_years": 10},
            "free_text": "fièvre, céphalées, myalgies, vomissements",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(7)}]},
            "medications": [{"name": "ibuprofène"}],
        })
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "ibuprofen" in forbidden
