"""Faïade service — délégation fine (V1 in-process, V2 = microservice)."""
from __future__ import annotations

from ..._bridge import register

register()


import importlib

_mod = importlib.import_module('ecp.engines.rollout_engine.engine')


plan_release = _mod.plan_release

gate_check = _mod.gate_check

evaluate_rollback_conditions = _mod.evaluate_rollback_conditions
