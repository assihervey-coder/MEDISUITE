"""Cas d'usage — création d'un change set immuable après approbation."""
from __future__ import annotations

from typing import Any

from ...domain.change.change_set import ChangeSet
from ...domain.change.change_unit import ChangeUnit
from ...domain.change.repository import ChangeSetRepository
from ...domain.proposal.value_objects import ChangeSetId


def create_change_set(proposal_id: str, baseline_version: str, baseline_commit: str,
                      target_version: str, units: list[dict[str, Any]],
                      migration_required: bool = False,
                      store: ChangeSetRepository | None = None) -> dict[str, Any]:
    cs_id = store.next_id() if store is not None else ChangeSetId("CHG-0000")
    cs = ChangeSet(
        id=cs_id, proposal=proposal_id,
        baseline_version=baseline_version, baseline_commit=baseline_commit,
        target_version=target_version,
        modifications=sorted({u["kind"] for u in units}),
        affected_components=sorted({u["component"] for u in units}),
        migration_required=migration_required)
    for u in units:
        cs.add_unit(ChangeUnit(kind=u["kind"], component=u["component"],
                               description=u.get("description", ""),
                               paths=list(u.get("paths", [])),
                               verify=u.get("verify", "")))
    checksum = cs.freeze()
    if store is not None:
        store.save(cs)
    return cs.to_dict()
