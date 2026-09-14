"""Typhoïde XDR — scénarios cliniques V1.2.

Couverture : retour de zone foyer (Pakistan/Asie du Sud), confirmation par
antibiogramme, orientation thérapeutique (azithromycine vs méropénème),
contre-indications (fluoroquinolones, céphalosporines), et contrôle négatif
hors zone XDR (comportement V1 inchangé).
"""
import pytest

from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestXDRTourDeZoneFoyer:
    def test_retour_pakistan_fievre_prolongee(self, days_ago):
        r = process_case({
            "patient": {"age_years": 28},
            "free_text": "fièvre depuis 8 jours, céphalées, douleurs abdominales, constipation",
            "travel": {"segments": [{"country": "PK", "departure": days_ago(35)}]},
            "vitals": {"temperature_c": 39.1},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "enteric_fever_xdr_risk" in codes, "drapeau XDR attendu après séjour au Pakistan"
        # différentiel : typhoïde
        diseases = {d["disease"] for d in r.differentials}
        assert "enteric_fever" in diseases
        # 1ère ligne XDR : azithromycine ; fluoroquinolone interdite
        recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        forb = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert "azithromycin" in recos
        assert "ciprofloxacin" in forb
        # ceftriaxone n'est PAS recommandée en contexte XDR
        assert "ceftriaxone" not in recos
        # hémoculture + antibiogramme requis
        tests = {t["test"] for t in r.required_tests}
        assert "antibiogram" in tests
        assert validate_response(r) == []

    def test_retour_inde_fievre_avec_contacts(self, days_ago):
        r = process_case({
            "patient": {"age_years": 33},
            "free_text": "fièvre depuis 5 jours, mon cousin était malade là-bas, céphalées",
            "travel": {"segments": [{"country": "IN", "sick_contacts": True,
                                      "departure": days_ago(25)}]},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "enteric_fever_xdr_contact" in codes


class TestXDRAntibiogramme:
    def test_xdr_confirme_forme_non_compliquee(self, days_ago):
        r = process_case({
            "patient": {"age_years": 26},
            "free_text": "fièvre depuis 10 jours, douleurs abdominales, céphalées",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(30)}]},
            "lab_results": [{"test": "antibiogram", "value": "xdr"}],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "enteric_fever_xdr_confirmed" in codes
        recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        forb = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        # forme non compliquée : azithromycine orale
        assert "azithromycin" in recos
        # XDR confirmé : FQ et céphalosporines interdites
        assert "ciprofloxacin" in forb
        assert "ceftriaxone" in forb
        # escalade hospitalière + signalement
        assert any(e["level"] == "refer_hospital" for e in r.escalations)

    def test_xdr_severe_meropeneme(self, days_ago):
        r = process_case({
            "patient": {"age_years": 45},
            "free_text": "fièvre depuis 12 jours, confusion, selles noires",
            "travel": {"segments": [{"country": "PK", "departure": days_ago(40)}]},
            "lab_results": [{"test": "antibiogram", "value": "xdr"}],
        })
        recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        # forme sévère (encéphalopathie + hémorragie digestive) : méropénème IV
        assert "meropenem" in recos
        # azithromycine orale seule non retenue
        assert "azithromycin" not in recos
        assert r.urgency in ("emergency", "immediate")

    def test_mdr_confirme_oriente_energetiquement(self, days_ago):
        r = process_case({
            "patient": {"age_years": 30},
            "free_text": "fièvre depuis 9 jours, céphalées, constipation",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(28)}]},
            "lab_results": [{"test": "antibiogram", "value": "mdr"}],
        })
        codes = [f["code"] for f in r.red_flags]
        assert "enteric_fever_mdr_confirmed" in codes


class TestXDRNegatifControle:
    def test_hors_zone_xdr_ceftriaxone_conservee(self, days_ago):
        """Hors zone XDR : le protocole standard (ceftriaxone) reste de mise."""
        r = process_case({
            "patient": {"age_years": 24},
            "free_text": "fièvre depuis 8 jours, céphalées, constipation, douleurs abdominales",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(30)}]},
        })
        recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "ceftriaxone" in recos
        codes = [f["code"] for f in r.red_flags]
        assert "enteric_fever_xdr_risk" not in codes
