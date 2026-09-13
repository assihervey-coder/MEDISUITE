"""Cas d'usage — plan de changement (units ordonnancées sans cycle)."""
from __future__ import annotations

from typing import Any

from ...domain.change.dependencies import topological_order
from ...domain.change.change_unit import ChangeUnit


def generate_change_plan(units: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = [ChangeUnit(kind=u["kind"], component=u["component"],
                         description=u.get("description", ""),
                         paths=list(u.get("paths", [])),
                         verify=u.get("verify", "")) for u in units]
    order = topological_order([(f"unit-{i}", list(u.get("depends_on", [])))
                               for i, u in enumerate(units)])
    return {
        "units": [u.to_dict() for u in parsed],
        "execution_order": order,
        "migration_units": [f"unit-{i}" for i, u in enumerate(units)
                            if u["kind"] == "MIGRATE"],
    }
