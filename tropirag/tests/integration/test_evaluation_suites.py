"""Tests de l'évaluation scientifique — métriques pures + suites complètes."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

# ---------------------------------------------------------------------------
# Métriques pures (sans I/O)
# ---------------------------------------------------------------------------


class TestRetrievalMetrics:

    def test_recall(self):
        from evaluation.retrieval.recall import mean_recall_at_k, reciprocal_rank
        assert reciprocal_rank(["a", "b", "c"], {"b"}) == 0.5
        assert reciprocal_rank(["a", "b"], {"z"}) == 0.0
        r = mean_recall_at_k([["a", "b"], ["c"]], [{"a", "b"}, {"c"}], 2)
        assert r == 1.0

    def test_precision(self):
        from evaluation.retrieval.precision import average_precision, precision_at_k
        assert precision_at_k(["a", "b", "c"], {"a", "c"}, 3) == 2 / 3
        ap = average_precision(["a", "x", "c"], {"a", "c"})
        assert abs(ap - (1 / 2) * (1 + 2 / 3)) < 1e-9

    def test_ndcg(self):
        from evaluation.retrieval.ndcg import mean_ndcg, ndcg
        # ordre parfait → nDCG = 1
        assert ndcg(["a", "b"], {"a": 2, "b": 1}) == 1.0
        # ordre inversé → nDCG < 1
        assert ndcg(["b", "a"], {"a": 2, "b": 1}) < 1.0
        assert mean_ndcg([["a"]], [{"a": 1}]) == 1.0


class TestDatasets:

    def test_datasets_charges(self):
        from evaluation.common import load_dataset
        clin = load_dataset("clinical_cases")
        adv = load_dataset("adversarial_cases")
        syn = load_dataset("synthetic_cases")
        assert len(clin) >= 8
        assert len(adv) >= 10
        assert len(syn) >= 6
        for item in clin:
            assert "payload" in item and "expect" in item

    def test_structure_attentes(self):
        from evaluation.common import load_dataset
        for item in load_dataset("clinical_cases"):
            exp = item["expect"]
            # au moins une attente vérifiable
            assert any(k in exp for k in
                       ("differential_in_top3", "top_differential", "urgency_at_least",
                        "escalation_includes", "suggested_tests_include"))


# ---------------------------------------------------------------------------
# Suites complètes (déterministes, offline)
# ---------------------------------------------------------------------------

class TestSuites:

    def test_retrieval_benchmark(self):
        from evaluation.retrieval.benchmark import run
        report = run()
        assert report.passed
        assert len(report.metrics) == 6

    def test_citation_accuracy(self):
        from evaluation.grounding.citation_accuracy import run
        assert run().passed

    def test_unsupported_claims(self):
        from evaluation.grounding.unsupported_claims import run
        assert run().passed

    def test_case_accuracy(self):
        from evaluation.clinical.case_accuracy import run
        report = run()
        assert report.passed
        assert report.metrics[0].value >= 0.90

    def test_escalation_quality(self):
        from evaluation.clinical.escalation_quality import run
        assert run().passed

    def test_model_benchmark(self):
        from evaluation.ai.model_benchmark import run
        assert run().passed

    def test_routing_benchmark(self):
        from evaluation.ai.routing_benchmark import run
        assert run().passed

    def test_memory_usage(self):
        from evaluation.ai.memory_usage import run
        assert run().passed

    def test_failure_rate(self):
        from evaluation.ai.failure_rate import run
        assert run().passed

    def test_refusal_benchmark(self):
        from evaluation.safety.refusal_benchmark import run
        assert run().passed

    def test_hallucination_benchmark(self):
        from evaluation.safety.hallucination_benchmark import run
        assert run().passed

    def test_dangerous_output(self):
        from evaluation.safety.dangerous_output_detection import run
        assert run().passed

    def test_safety_invariants(self):
        from evaluation.safety.safety_benchmark import run
        assert run().passed

    def test_rapports_ecrits(self):
        from evaluation.common import REPORTS_DIR
        jsons = list(REPORTS_DIR.rglob("*_report.json"))
        assert len(jsons) >= 14  # chaque suite a écrit son rapport
        md = list(REPORTS_DIR.rglob("*_report.md"))
        assert len(md) >= 14
