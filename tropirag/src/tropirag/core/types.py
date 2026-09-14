"""Types utilitaires partagés (alias de lisibilité)."""
from __future__ import annotations
from typing import Any, TypeAlias

JSON: TypeAlias = dict[str, "JSONValue"]
JSONValue: TypeAlias = Any
Meta: TypeAlias = dict[str, str]
