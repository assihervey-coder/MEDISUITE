"""Faïade service — délégation fine (V1 in-process, V2 = microservice)."""
from __future__ import annotations

from ..._bridge import register

register()


import importlib

_mod = importlib.import_module('ecp.application.planning.generate_test_plan')


generate_test_plan = _mod.generate_test_plan
