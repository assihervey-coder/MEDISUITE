"""Verrou : rollout (stratégie, stages, gates, SLO) + rollback (triggers, checkpoints)."""
from __future__ import annotations

import pytest

from ecp.engines.rollout_engine.engine import (evaluate_rollback_conditions,
                                               gate_check, plan_release)
from ecp.domain.rollout.feature_flags import FeatureFlag, demote_to_off, promote
from ecp.domain.rollout.monitoring import Metrics, SloEvaluator
from ecp.domain.rollout.stages import RolloutPlan
from ecp.domain.rollback.checkpoints import CheckpointSet
from ecp.domain.rollback.recovery import recovery_plan
from ecp.domain.rollback.strategy import (CheckpointsIncomplete,
                                          REQUIRED_CHECKPOINTS, assert_rollback_ready)
from ecp.domain.rollback.triggers import evaluate_triggers


def test_strategie_par_classe():
    assert plan_release("REL-9001", "P3")["strategy"]["strategy"] in ("staged", "direct")
    assert plan_release("REL-9002", "P4")["strategy"]["strategy"] == "canary"
    assert plan_release("REL-9003", "P7")["strategy"]["strategy"] == "pilot"


def test_progression_stages_sans_saut():
    plan = RolloutPlan("REL-9004", ["staging", "pilot", "canary-10%"])
    assert plan.current.name == "staging"
    stage = plan.advance()
    assert stage.name == "pilot" and plan.stages[0].status == "PASSED"
    plan.advance()
    plan.advance()
    assert plan.finished


def test_gates_bloquants():
    assert gate_check(["smoke", "regression"], {"smoke"})["gates"] == "FAIL"
    assert gate_check(["smoke"], {"smoke", "regression"})["gates"] == "PASS"


def test_slo_p95_deux_secondes_egsp():
    evaluator = SloEvaluator()
    ok, _ = evaluator.evaluate(Metrics(error_rate=0.001, latency_p95_ms=1500))
    assert ok
    bad, breaches = evaluator.evaluate(Metrics(error_rate=0.02, latency_p95_ms=2500))
    assert not bad and len(breaches) == 2


def test_flags_progression_et_rollback_off():
    f = FeatureFlag("patient_digital_twin")
    f2 = promote(f)
    assert f2.state == "DEV"
    assert demote_to_off(promote(f2, steps=5)).state == "OFF"
    with pytest.raises(ValueError):
        FeatureFlag("x", "P1337")


def test_declencheurs_rollback():
    assert evaluate_triggers({}, []) == []
    triggers = evaluate_triggers({"error_rate": 0.05, "latency_p95_ms": 3000,
                                  "model_psi": 0.3},
                                 ["clinical_safety"], human_decision=True)
    names = {t.name for t in triggers}
    assert {"error_rate", "latency_p95", "model_drift", "clinical_safety",
            "human_decision"} <= names


def test_rollback_sans_checkpoints_complets_interdit():
    with pytest.raises(CheckpointsIncomplete):
        assert_rollback_ready({"previous_version"})


def test_sept_checkpoints_obligatoires():
    assert len(REQUIRED_CHECKPOINTS) == 7
    cp = CheckpointSet("REL-9005")
    for i, name in enumerate(REQUIRED_CHECKPOINTS):
        cp.add(name, f"artifact-{i}")
    assert cp.ready is True


def test_ordre_de_recuperation_flags_dabord():
    plan = recovery_plan(list(REQUIRED_CHECKPOINTS))
    assert plan["order"][0] == "feature_flag_state"
    assert plan["missing"] == []


def test_condition_rollback_moteur():
    result = evaluate_rollback_conditions({"error_rate": 0.2}, [])
    assert result["rollback_required"] and result["triggers"][0]["name"] == "error_rate"
