"""Tests de normalisation des symptômes — la fondation du déterminisme."""
import pytest

from tropirag.domain.symptoms.normalization import normalize_symptoms, parse_symptom_entries
from tropirag.domain.symptoms.taxonomy import SYMPTOMS


def codes(text: str) -> list[str]:
    return [s.code for s in normalize_symptoms(text)]


class TestExtractionFrancais:
    def test_fievre_simple(self):
        assert "fever" in codes("le patient a de la fièvre")

    def test_fievre_elevee_explicite(self):
        found = codes("fièvre élevée à 40")
        assert "high_fever" in found

    def test_temperature_39_6(self):
        assert "high_fever" in codes("fièvre 39,6 depuis 3 jours")

    def test_temperature_38_2(self):
        found = codes("T° 38.2 ce matin")
        assert "fever" in found and "high_fever" not in found

    def test_temperature_normale_ignoree(self):
        assert "fever" not in codes("le patient pèse 70 kg et mesure 1,75 m, apyrétique 36,8")

    def test_triade_palustre(self):
        found = codes("frissons, céphalées et vomissements")
        assert {"chills", "headache", "vomiting"} <= set(found)

    def test_argot_clinique(self):
        found = codes("le corps casse, il rend tout, corps chaud")
        assert "myalgia" in found and "vomiting" in found and "fever" in found

    def test_hemorragiques(self):
        found = codes("saignements des gencives, selles noires, urines foncées")
        assert {"bleeding_gums", "melena", "dark_urine"} <= set(found)

    def test_neuro(self):
        found = codes("il est confus, nuque raide")
        assert {"confusion", "neck_stiffness"} <= set(found)

    def test_douleur_retro_orbitaire(self):
        assert "retro_orbital_pain" in codes("douleur derrière les yeux")


class TestSeverite:
    def test_qualificatif_severe(self):
        found = normalize_symptoms("vomissements incoercibles et importants")
        vom = [s for s in found if s.code == "vomiting"]
        assert vom and vom[0].severity == "severe"

    def test_simple_present(self):
        found = normalize_symptoms("quelques vomissements")
        vom = [s for s in found if s.code == "vomiting"]
        assert vom and vom[0].severity == "present"


class TestEntreesStructurees:
    def test_parse_entries(self):
        entries = [
            {"code": "fever", "onset": "2026-09-01", "duration": "3 jours"},
            {"code": "inconnu_xyz", "severity": "severe"},  # ignoré
        ]
        out = parse_symptom_entries(entries)
        assert len(out) == 1 and out[0].code == "fever"
        assert out[0].duration_days == 3.0

    def test_stabilite(self):
        """Même entrée → même sortie (reproductibilité)."""
        a = codes("fièvre, frissons, céphalées")
        b = codes("fièvre, frissons, céphalées")
        assert a == b

    def test_vide(self):
        assert normalize_symptoms("") == []
        assert normalize_symptoms(None) == []


class TestTaxonomie:
    def test_tous_les_codes_decores(self):
        for code, meta in SYMPTOMS.items():
            assert meta["fr"], f"{code} sans label FR"
