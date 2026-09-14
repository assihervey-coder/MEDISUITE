"""Méningocoque pédiatrique — scénarios cliniques V1.3.

Couverture : nourrisson (fontanelle bombée — méningite sans raideur de nuque),
petit enfant (irritabilité/refus alimentaire), purpura fulminans (ceftriaxone
IM AVANT transfert), sepsis grave, prophylaxie des contacts (notification),
et contrôles négatifs (adulte sans signe pédiatrique, âge inconnu).
"""
import pytest

from tropirag.response_engine.response_orchestrator import process_case
from tropirag.response_engine.response_validator import validate_response


class TestNourrisson:
    def test_fontanelle_bombee_fievre(self):
        r = process_case({
            "patient": {"age_months": 9, "sex": "male"},
            "free_text": "bébé fiévreux depuis 2 jours, pleure sans arrêt, "
                         "refuse le biberon, fontanelle bombée",
            "vitals": {"temperature_c": 39.2},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "pediatric_meningitis_fontanelle" in codes, (
            "fontanelle bombée + fièvre chez le nourrisson → méningite")
        assert r.severity == "critical"
        # transfert urgent + PL/hémoculture
        assert any(e["level"] == "emergency_transfer" for e in r.escalations)
        tests = {t["test"] for t in r.required_tests}
        assert {"lp", "blood_culture_men"} <= tests
        diseases = {d["disease"] for d in r.differentials}
        assert "meningococcal" in diseases
        assert validate_response(r) == []

    def test_signes_non_specifiques_petit_enfant(self):
        r = process_case({
            "patient": {"age_years": 2},
            "free_text": "fièvre, enfant très agité, inconsolable, ne mange plus",
            "vitals": {"temperature_c": 39.0},
        })
        diseases = {d["disease"] for d in r.differentials}
        assert "meningococcal" in diseases, (
            "fièvre + irritabilité/refus alimentaire < 5 ans → IIM possible")


class TestPurpuraFulminans:
    def test_purpura_enfant_ceftriaxone_avant_transfert(self):
        r = process_case({
            "patient": {"age_years": 3},
            "free_text": "fièvre élevée depuis ce matin, taches violettes sur les jambes, "
                         "très abattu, vomit",
            "vitals": {"temperature_c": 39.8},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "pediatric_purpura_fulminans" in codes, (
            "'taches violettes' doit normaliser en petechiae → purpura fulminans")
        assert r.urgency == "immediate" and r.severity == "critical"
        assert any(e["level"] == "emergency_transfer" for e in r.escalations)
        # antibiothérapie : la recommandation ceftriaxone est portée par les règles
        recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
        assert "ceftriaxone" in recos, "ceftriaxone recommandée (IIM)"
        assert validate_response(r) == []

    def test_sepsis_grave_enfant(self):
        r = process_case({
            "patient": {"age_years": 5},
            "free_text": "fièvre, prostré, convulsions ce matin, pâle, vomit",
            "vitals": {"temperature_c": 39.4},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "pediatric_sepsis_meningococcal" in codes
        assert r.urgency == "immediate"


class TestProphylaxie:
    def test_notification_prophylaxie_contacts(self):
        r = process_case({
            "patient": {"age_years": 4},
            "free_text": "raideur de nuque, fièvre, photophobie, vomit",
            "vitals": {"temperature_c": 39.6},
        })
        notifs = " ".join(str(n) for n in r.notifications).lower()
        assert "prophyla" in notifs or "public" in notifs, (
            "la notification IIM pédiatrique inclut la prophylaxie des contacts")


class TestControlesNegatifs:
    def test_adulte_sans_drapeau_pediatrique(self):
        r = process_case({
            "patient": {"age_years": 40},
            "free_text": "fièvre et céphalées depuis 2 jours",
            "vitals": {"temperature_c": 38.5},
        })
        codes = [f["code"] for f in r.red_flags]
        assert "pediatric_purpura_fulminans" not in codes
        assert "pediatric_meningitis_fontanelle" not in codes

    def test_age_inconnu_ne_declenche_pas_les_regles_agees(self):
        r = process_case({
            "patient": {},
            "free_text": "fièvre, taches violettes, abattu",
            "vitals": {"temperature_c": 39.0},
        })
        codes = [f["code"] for f in r.red_flags]
        # âge inconnu → patient_age indéterminable → règles pédiatriques suspendues
        assert "pediatric_purpura_fulminans" not in codes, (
            "l'âge inconnu ne doit pas déclencher une règle âge-dépendante")
        # mais le purpura fébrile générique reste actif (sécurité maintenue)
        assert "petechiae" in codes, "le drapeau purpura générique reste posé"
