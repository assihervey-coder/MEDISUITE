"""Adapter OpenBioLLM — normalisation + neutralisation prudente des sorties.

Défense en profondeur : même avant les guards, les verbes assertifs les plus
dangereux sont reformulés en formes prudentes. Le Safety Gate reste
l'autorité finale — cette passe ne fait que réduire le bruit.
"""
from __future__ import annotations

import re
from typing import Any

# verbes assertifs → formes prudentes (défense en profondeur, pré-garde)
_HEDGING = [
    (r"\bconfirme\b", "suggère la possibilité de"),
    (r"\bgarantit\b", "peut évoquer"),
    (r"\bc'est certain\b", "il est possible"),
    (r"\bdiagnostic certain\b", "hypothèse diagnostique"),
    (r"\bassurément\b", "possiblement"),
]


def hedge(text: str) -> str:
    out = text
    for pattern, replacement in _HEDGING:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    return out


def parse_synthesis(structured: Any) -> dict:
    if not isinstance(structured, dict):
        return {"synthesis": "", "themes": [], "gaps": [], "citations": [],
                "hedges_applied": 0, "parse_ok": False}
    synthesis = hedge(str(structured.get("synthesis", "")))
    themes = [hedge(str(x)) for x in structured.get("themes", [])]
    gaps = [str(x) for x in structured.get("gaps", [])]
    citations = [str(c) for c in structured.get("citations", [])]
    # citations dédupliquées, format EU-* préservé
    seen: set[str] = set()
    unique_citations = [c for c in citations if not (c in seen or seen.add(c))]
    return {"synthesis": synthesis, "themes": themes, "gaps": gaps,
            "citations": unique_citations,
            "hedges_applied": sum(1 for p, _ in _HEDGING
                                   if re.search(p, str(structured.get("synthesis", "")),
                                                flags=re.IGNORECASE)),
            "parse_ok": True}
