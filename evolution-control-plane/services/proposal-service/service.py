"""Faïade service — délégation fine (V1 in-process, V2 = microservice)."""
from __future__ import annotations

from ..._bridge import register

register()


import importlib

_mod = importlib.import_module('ecp.api.rest.proposals')


router = _mod.router
