"""Scénarios cliniques bout-en-bout — fièvre + voyage (Afrique de l'Ouest).

Chaque scénario vérifie : différentiel prioritaire, red flags, escalade,
tests requis, contraintes médicamenteuses, citations.
"""
import pytest

from tropirag.core.enums import Severity, Urgency
from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestScenario1PaludismeSimple:
    def test_fievre_retour_ci(self, fever_travel_ci_case):
        r = process_case(fever_travel_ci_case())
        # différentiel : paludisme en tête
        assert r.differentials[0]["disease"] == "malaria"
        assert r.differentials[0]["score"] >= 0.4
        # tests requis : TDR + goutte épaisse
        tests = {t["test"] for t in r.required_tests}
        assert "rdt_malaria" in tests and "thick_smear" in tests
        # citations présentes
        assert r.citations, "aucune citation"
        assert any("who" in c["unit_id"] or "ci" in c["unit_id"] for c in r.citations)
        # structure valide
        assert validate_response(r) == []


class TestScenario2PaludismeSevere:
    def test_neuropaludisme(self, days_ago):
        r = process_case({
            "patient": {"age_years": 42},
            "free_text": "fièvre 40,2, convulsions puis coma, prostration",
            "travel": {"segments": [{"country": "BF", "rural_stay": True,
                                      "departure": days_ago(8)}]},
            "vitals": {"temperature_c": 40.2},
        })
        assert r.urgency in ("emergency", "immediate")
        assert r.severity in ("severe", "critical")
        # red flag paludisme cérébral
        flags = " ".join(f["code"] for f in r.red_flags)
        assert "cerebral_malaria" in flags
        # pas de synthèse IA en cas critique (déterministe pur)
        assert r.ai_synthesis is None

    def test_anemie_severe(self, days_ago):
        r = process_case({
            "patient": {"age_years": 7},
            "free_text": "fièvre depuis 5 jours, pâleur intense",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(20)}]},
            "lab_results": [{"test": "cbc", "component": "hb", "numeric": 5.8, "unit": "g/dL"}],
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "severe_anemia_malaria" in codes_


class TestScenario3DengueAlarme:
    def test_signes_alarme_oms(self, days_ago):
        r = process_case({
            "patient": {"age_years": 29},
            "free_text": "fièvre 39,5, céphalées, douleur derrière les yeux, "
                        "douleurs abdominales importantes, vomissements incoercibles",
            "travel": {"segments": [{"country": "CI", "region": "Abidjan",
                                      "departure": days_ago(10)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert any("dengue_warning" in c for c in codes_)
        # AINS interdits
        forbidden = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
        assert {"ibuprofen", "aspirin", "diclofenac"} <= forbidden
        # paracétamol recommandé
        allowed = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "paracetamol" in allowed

    def test_thrombopenie_orient_dengue(self, days_ago):
        r = process_case({
            "patient": {"age_years": 35},
            "free_text": "fièvre, myalgies, céphalées",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(7)}]},
            "lab_results": [{"test": "cbc", "component": "plt", "numeric": 72000, "unit": "/µL"}],
        })
        diseases = [d["disease"] for d in r.differentials]
        assert "dengue" in diseases


class TestScenario4Typhoide:
    def test_fievre_prolongee_digestive(self, days_ago):
        r = process_case({
            "patient": {"age_years": 24},
            "free_text": "fièvre depuis 8 jours, douleurs abdominales, constipation, céphalées",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(30)}]},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "enteric_fever" in diseases
        tests = {t["test"] for t in r.required_tests}
        assert "blood_culture" in tests


class TestScenario5FievreJaune:
    def test_ictere_zone_amarile(self, days_ago):
        r = process_case({
            "patient": {"age_years": 50},
            "free_text": "fièvre, ictère, urines foncées",
            "travel": {"segments": [{"country": "GH", "departure": days_ago(6)}]},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "yellow_fever" in diseases
        # notification obligatoire
        assert r.notifications, "fièvre jaune sans notification"
        assert any("obligatoire" in n["reason"].lower() or "d[ée]claration" in n["reason"].lower()
                   for n in r.notifications)


class TestScenario6MVHEbola:
    def test_fievre_zone_epidemie(self, days_ago):
        r = process_case({
            "patient": {"age_years": 31},
            "free_text": "fièvre 39, myalgies",
            "travel": {"segments": [{"country": "GN", "departure": days_ago(15),
                                       "burial_attended": True}]},
        })
        # isolement + notification + urgence
        assert r.urgency in ("emergency", "immediate")
        assert any("ISOLEMENT" in e["message"].upper() or e["level"] == "isolation"
                   for e in r.escalations)
        codes_ = [f["code"] for f in r.red_flags]
        assert any("vhf" in c for c in codes_)

    def test_saignements_inexpliques_21j(self, days_ago):
        r = process_case({
            "patient": {"age_years": 38},
            "free_text": "fièvre et saignements anormaux",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(12)}]},
        })
        codes_ = [f["code"] for f in r.red_flags]
        assert "vhf_generic_suspected" in codes_


class TestScenario7Meninigte:
    def test_raideur_nuque(self):
        r = process_case({
            "patient": {"age_years": 19},
            "free_text": "fièvre 40, raideur de nuque, vomissements, photophobie",
        })
        assert r.urgency == "immediate"
        diseases = {d["disease"] for d in r.differentials}
        assert "meningococcal" in diseases
        assert any("ceftriaxone" in e["message"].lower() for e in r.escalations)


class TestScenario8GrossesseZika:
    def test_zika_enceinte_orientation(self, days_ago):
        r = process_case({
            "patient": {"age_years": 23, "sex": "female", "pregnant": "pregnant"},
            "free_text": "fièvre modérée, éruption, yeux rouges, arthralgies",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(9)}]},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "zika" in diseases
        assert any("enceinte" in e["message"].lower() or "grossesse" in e["message"].lower()
                   for e in r.escalations)


class TestStructureReponse:
    def test_disclaimer_toujours_present(self, days_ago):
        r = process_case({
            "patient": {"age_years": 30},
            "free_text": "fièvre",
            "travel": {"segments": [{"country": "CI", "departure": days_ago(5)}]},
        })
        assert "professionnels de santé" in r.disclaimer

    def test_provenance_trace(self, fever_travel_ci_case):
        r = process_case(fever_travel_ci_case())
        assert r.provenance["matched_rule_ids"]
        assert r.provenance["evidence_units"]

    def test_determinisme_meme_entree_meme_sortie(self, fever_travel_ci_case):
        a = process_case(fever_travel_ci_case())
        b = process_case(fever_travel_ci_case())
        assert a.narrative == b.narrative
        assert [d["disease"] for d in a.differentials] == [d["disease"] for d in b.differentials]
