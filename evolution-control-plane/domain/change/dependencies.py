"""Dépendances entre units — ordonnancement sans cycle."""
from __future__ import annotations


def topological_order(units: list[tuple[str, list[str]]]) -> list[str]:
    """units : [(unit_id, depends_on_ids)] — ordre d'exécution sûr.

    Lève ValueError en cas de cycle ou de dépendance inconnue.
    """
    known = {u for u, _ in units}
    deps = {u: list(d) for u, d in units}
    for u, d in deps.items():
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"dépendances inconnues pour {u} : {sorted(unknown)}")
    order: list[str] = []
    state: dict[str, int] = {}  # 0=blanc 1=gris 2=noir

    def visit(u: str) -> None:
        st = state.get(u, 0)
        if st == 1:
            raise ValueError("cycle de dépendances détecté")
        if st == 2:
            return
        state[u] = 1
        for d in deps[u]:
            visit(d)
        state[u] = 2
        order.append(u)

    for u in deps:
        visit(u)
    return order
