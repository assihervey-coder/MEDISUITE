"""Lignage — de la requête à la réponse, qui a contribué quoi."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LineageNode:
    node_id: str
    kind: str
    detail: str
    children: list["LineageNode"] = field(default_factory=list)


def add_child(parent: LineageNode, child: LineageNode) -> LineageNode:
    parent.children.append(child)
    return child
