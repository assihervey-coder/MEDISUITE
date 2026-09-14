"""Tests décision/temporel/query enrichis (Phase squelettes comblés)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tropirag.clinical_engine.decision_context import (  # noqa: E402
    DecisionContext,
    build_decision_context,
)
from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator  # noqa: E402
from tropirag.domain.clinical_case.builders import build_case  # noqa: E402
from tropirag.query_engine.evidence_requirements import (  # noqa: E402
    check_evidence_requirement,
)
from tropirag.query_engine.intent_classifier import classify, classify_intent  # noqa: E402
from tropirag.query_engine.jurisdiction_filter import (  # noqa: E402
    filter_by_jurisdiction,
    jurisdiction_ok,
)
from tropirag.query_engine.temporal_filter import (  # noqa: E402
    recency_factor,
    sort_by_recency,
)

CASE = {
    "case_id": "ctx-1",
    "patient": {"age": 30, "sex": "male"},
    "symptoms": [{"code": "fever", "onset": "2026-09-08"},
                 {"code": "headache"}, {"code": "chills"}],
    "travel": {"segments": [
        {"country": "CI", "region": "lagunes",
         "arrival": "2026-08-20", "departure": "2026-09-05"}]},
    "lab_results": [{"code": "rdt_malaria", "result": "positive"}],
    "consultation_date": "2026-09-10",
}


class TestDecisionContext:

    def test_construction_depuis_analyse(self):
        analysis = ClinicalOrchestrator().analyze_payload(CASE)
        ctx = build_decision_context(analysis)
        assert ctx.case_id == "ctx-1"
        assert "fever" in ctx.symptom_codes
        assert ctx.matched_rules  # le paludisme doit matcher
        rendered = ctx.render()
        assert "CAS ctx-1" in rendered
        assert "fever" in rendered

    def test_render_sans_donnees_sensibles_brutes(self):
        ctx = DecisionContext(case_id="x", symptom_codes=["fever"])
        out = ctx.render()
        assert "x" in out and "fever" in out


class TestTimelineEngine:

    def test_coherence_ok(self):
        from tropirag.clinical_engine.temporal.timeline_engine import TimelineEngine
        report = TimelineEngine().build(build_case(CASE))
        assert report.coherent
        kinds = {e.kind for e in report.events}
        assert {"exposure", "symptom", "consultation"} <= kinds
        dates = [e.date for e in report.events]
        assert dates == sorted(dates)  # tri chronologique

    def test_incoherence_detectee(self):
        from tropirag.clinical_engine.temporal.timeline_engine import TimelineEngine
        bad = dict(CASE)
        bad["travel"] = {"segments": [
            {"country": "CI", "arrival": "2026-09-05", "departure": "2026-08-20"}]}
        report = TimelineEngine().build(build_case(bad))
        assert not report.coherent
        assert any("antérieur à l'arrivée" in i for i in report.incoherences)

    def test_symptome_avant_retour(self):
        from tropirag.clinical_engine.temporal.timeline_engine import TimelineEngine
        bad = dict(CASE)
        bad["symptoms"] = [{"code": "fever", "onset": "2026-09-01"}]  # avant le retour
        report = TimelineEngine().build(build_case(bad))
        assert any("AVANT le retour" in i for i in report.incoherences)


class TestIntentClassifier:

    def test_intentions(self):
        assert classify_intent("ce médicament est-il sûr pendant la grossesse ?") == "drug_check"
        assert classify_intent("qu'est-ce que la dengue ?") == "info"
        assert classify_intent("montre-moi la source OMS sur l'artésunate") == "evidence_search"
        assert classify_intent("pose un diagnostic pour moi") == "unsafe"
        assert classify_intent("homme fièvre 39 vomissements depuis 2 jours") == "clinical_analysis"

    def test_classify_detaille(self):
        out = classify("peut-on donner cet antibiotique avec ce traitement ?")
        assert out["intent"] == "drug_check" and out["signals"]


class TestJurisdictionFilter:

    def test_applicabilite(self):
        assert jurisdiction_ok("INT", "CI")
        assert jurisdiction_ok("CI", "CI")
        assert jurisdiction_ok("SN", "CI")       # corridor régional
        assert not jurisdiction_ok("SN", "CI", regional=False)
        assert not jurisdiction_ok("PK", "CI")   # hors corridor

    def test_filtre_units(self):
        class U:
            def __init__(self, j, i):
                self.jurisdiction, self.unit_id = j, i
        units = [U("INT", "a"), U("CI", "b"), U("SN", "c"), U("PK", "d")]
        out = filter_by_jurisdiction(units, "CI")
        assert [u.unit_id for u in out] == ["a", "b", "c"]


class TestTemporalFilter:

    def test_facteur_fraicheur(self):
        class S:
            def __init__(self, y):
                self.edition_date = f"{y}-01-01" if y else None
        assert recency_factor(S(2026)) == 1.0
        assert recency_factor(S(2015)) == 0.3
        assert recency_factor(S(None)) == 0.8
        mid = recency_factor(S(2021))
        assert 0.3 < mid < 1.0

    def test_tri_recence(self):
        class S:
            def __init__(self, y):
                self.edition_date = f"{y}-01-01"
        class U:
            def __init__(self, y, i):
                self.source, self.unit_id = S(y), i
        out = sort_by_recency([U(2020, "a"), U(2024, "b"), U(2022, "c")])
        assert [u.unit_id for u in out] == ["b", "c", "a"]


class TestEvidenceRequirements:

    def test_pack_insuffisant(self):
        from tropirag.core.enums import SourceAuthority
        from tropirag.domain.evidence.entities import EvidencePack, EvidenceUnit, SourceRef

        sci = SourceRef(source_id="s", authority=SourceAuthority.SCIENTIFIC,
                        title="Étude", publisher="Journal")
        pack = EvidencePack(query="q")
        pack.units = [EvidenceUnit(unit_id="eu-s", text="x", source=sci)]
        check = check_evidence_requirement(pack, "clinical_analysis")
        assert not check.passed
        assert "insuffisant" in check.reason

    def test_pack_suffisant(self):
        from tropirag.core.enums import SourceAuthority
        from tropirag.domain.evidence.entities import EvidencePack, EvidenceUnit, SourceRef

        who = SourceRef(source_id="w", authority=SourceAuthority.WHO,
                        title="Guide", publisher="OMS")
        pack = EvidencePack(query="q")
        pack.units = [EvidenceUnit(unit_id="eu-w", text="x", source=who)]
        check = check_evidence_requirement(pack, "clinical_analysis")
        assert check.passed and check.units_accepted == 1

    def test_pack_vide_refuse(self):
        from tropirag.domain.evidence.entities import EvidencePack

        check = check_evidence_requirement(EvidencePack(query="q"), "info")
        assert not check.passed


class TestDiseaseModules:

    def test_modules_maladie_exposes(self):
        from tropirag.clinical_engine.diseases.malaria.module import (
            available_summaries,
            module_info,
        )
        info = module_info()
        assert info["label_fr"] == "Paludisme"
        assert "severe_criteria_summary" in available_summaries()
