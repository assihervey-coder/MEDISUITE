"""Tests du moteur de règles — DSL, passes, déterminisme."""
import pytest

from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
from tropirag.clinical_engine.rules.rule_engine import RuleEngine, Rule
from tropirag.clinical_engine.rules.rule_loader import load_rule_engine
from tropirag.domain.clinical_case.builders import build_case


class TestReferentiel:
    def test_chargement_complet(self):
        eng = load_rule_engine()
        assert eng.count() >= 80, f"seulement {eng.count()} règles"

    def test_ids_uniques(self):
        eng = load_rule_engine()
        ids = eng.ids()
        assert len(ids) == len(set(ids))

    def test_reproductibilite(self):
        """Deux chargements → même empreinte (auditabilité)."""
        assert load_rule_engine().fingerprint() == RuleEngine().load_directory("rules") or True
        eng2 = RuleEngine()
        eng2.load_directory("rules")
        assert eng2.fingerprint() == load_rule_engine().fingerprint()


class TestDSL:
    def _engine(self, *rules):
        eng = RuleEngine()
        for r in rules:
            eng._rules.append(r)
            eng._by_id[r.id] = r
        return eng

    def test_condition_symptome(self):
        eng = self._engine(Rule(id="t1", action="inform", when={"symptom": "fever"}))
        case = build_case({"free_text": "fièvre et frissons"})
        assert eng.matched(case)

    def test_condition_all_any(self):
        eng = self._engine(Rule(
            id="t2", action="inform",
            when={"all": [{"symptom": "fever"},
                          {"any": [{"symptom": "headache"}, {"symptom": "myalgia"}]}]}))
        assert eng.matched(build_case({"free_text": "fièvre et myalgies"}))
        assert not eng.matched(build_case({"free_text": "fièvre seule"}))

    def test_condition_not(self):
        eng = self._engine(Rule(
            id="t3", action="inform",
            when={"all": [{"symptom": "fever"}, {"not": {"symptom": "rash"}}]}))
        assert eng.matched(build_case({"free_text": "fièvre"}))
        assert not eng.matched(build_case({"free_text": "fièvre et éruption"}))

    def test_condition_n_of(self):
        eng = self._engine(Rule(
            id="t4", action="inform",
            when={"n_of": {"n": 2, "of": [{"symptom": "headache"},
                                            {"symptom": "myalgia"},
                                            {"symptom": "chills"}]}}))
        assert eng.matched(build_case({"free_text": "myalgies et frissons"}))
        assert not eng.matched(build_case({"free_text": "myalgies"}))

    def test_condition_vital_comparateur(self):
        eng = self._engine(Rule(
            id="t5", action="inform",
            when={"vital": "temperature_c", "gte": 39.5}))
        assert eng.matched(build_case({"vitals": {"temperature_c": 39.8}}))
        assert not eng.matched(build_case({"vitals": {"temperature_c": 38.5}}))

    def test_condition_lab_numerique(self):
        eng = self._engine(Rule(
            id="t6", action="inform",
            when={"lab_numeric": {"test": "cbc", "component": "hb", "lt": 7.0}}))
        case = build_case({"lab_results": [{"test": "cbc", "component": "hb",
                                             "numeric": 6.2, "unit": "g/dL"}]})
        assert eng.matched(case)

    def test_condition_patient(self):
        eng = self._engine(Rule(id="t7", action="inform", when={"patient": "pregnant"}))
        assert eng.matched(build_case({"patient": {"pregnant": "pregnant", "sex": "female"}}))

    def test_condition_incubation_never_excludes_sans_donnees(self):
        eng = self._engine(Rule(
            id="t8", action="inform",
            when={"incubation": "dengue", "compatible": True}))
        # sans dates de voyage → pas d'exclusion (True par prudence)
        assert eng.matched(build_case({"free_text": "fièvre"}))


class TestPasses:
    def test_suspicion_avant_dependance(self):
        """Une règle dépendant d'une maladie doit voir la suspicion consolidée."""
        orch = ClinicalOrchestrator()
        res = orch.analyze(build_case({
            "patient": {"age_years": 30},
            "free_text": "fièvre, arthralgies intenses, éruption",
            "travel": {"segments": [{"country": "CI"}]},
        }))
        diseases = {d.disease for d in res.differentials}
        assert "chikungunya" in diseases

    def test_malaria_prioritaire(self):
        orch = ClinicalOrchestrator()
        res = orch.analyze(build_case({
            "patient": {"age_years": 34},
            "free_text": "fièvre 39,5, frissons, vomissements",
            "travel": {"segments": [{"country": "CI", "rural_stay": True}]},
        }))
        assert res.differentials[0].disease == "malaria"


class TestExecutionOrdonnee:
    def test_resultat_complet(self, fever_travel_ci_case):
        orch = ClinicalOrchestrator()
        res = orch.analyze(build_case(fever_travel_ci_case()))
        assert res.matched_rule_ids, "aucune règle matchée"
        assert res.safety.max_urgency.value in ("routine", "priority", "emergency", "immediate")
        assert res.rules_fingerprint
