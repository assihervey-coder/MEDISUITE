"""Faïade service — délégation fine (V1 in-process, V2 = microservice)."""
from __future__ import annotations

from ..._bridge import register

register()


import importlib

_mod = importlib.import_module('ecp.engines.test_impact_engine.dependency_mapper')


dependency_mapper = _mod.dependency_mapper
