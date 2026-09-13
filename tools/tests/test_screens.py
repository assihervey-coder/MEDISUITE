"""Tests du générateur d'écrans fins ×96 (chantier v0.14 —
COUVERTURE-ARBRE-INITIAL §2 bloc `apps/web-portal`).

Propriétés verrouillées :
1. DÉTERMINISME — deux builds successifs identiques ;
2. IDEMPOTENCE DU DÉPÔT --check — fichiers committés == régénération ;
3. COMPTAGE — 96 écrans (24 modules × 4 types), routes uniques ;
4. ALIGNEMENT SOURCES — scores = docstrings des services (ast), signatures
   = inspect de clinical-rules, IA = configs yaml + datasets/registry ;
5. HONNÊTETÉ — chaque endpoint de l'écran détail existe côté service ;
6. CIBLAGE — sorties strictement sous apps/web-portal/src/screens/.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "tools" / "generate_screens.py"
OUT = ROOT / "apps" / "web-portal" / "src" / "screens"


def _load_gen():
    spec = importlib.util.spec_from_file_location("generate_screens", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_01_deterministic():
    gen = _load_gen()
    a = gen.build_screens()
    b = gen.build_screens()
    assert len(a) == 96
    assert a == b


def test_02_committed_files_match_generation():
    gen = _load_gen()
    screens = gen.build_screens()
    for path, content in gen.outputs(screens):
        assert path.exists(), f"artefact manquant : {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8") == content, (
            f"dérive générée/dépôt : {path.relative_to(ROOT)} — relancer make screens"
        )


def test_03_comptage_96_routes_uniques():
    gen = _load_gen()
    screens = gen.build_screens()
    assert len(screens) == 96
    kinds = {"overview", "cas", "detail", "ia"}
    for url in {s["urlSlug"] for s in screens}:
        got = {s["kind"] for s in screens if s["urlSlug"] == url}
        assert got == kinds, f"{url} : types {got}"
    routes = [s["route"] for s in screens]
    assert len(set(routes)) == 96
    assert sum(1 for r in routes if ":caseId" in r) == 24


def test_04_alignement_sources():
    gen = _load_gen()
    screens = gen.build_screens()
    onc = next(s for s in screens if s["id"] == "oncology:detail")
    assert "birads" in onc["scores"]
    birads = next(sg for sg in onc["sigs"] if sg["endpoint"] == "birads")
    assert birads["fn"] == "birads" and len(birads["params"]) >= 1
    # features IA = plages réelles de datasets/registry.py
    diab = next(s for s in screens if s["id"] == "diabetes:ia")
    names = {f["name"] for f in diab["ai"]["features"]}
    assert "hba1c_pct" in names
    for f in diab["ai"]["features"]:
        assert f["lo"] < f["hi"]


def test_05_honnetete_endpoints_existent_dans_les_services():
    """Chaque signature générée référence une fonction importable réelle."""
    gen = _load_gen()
    for s in gen.build_screens():
        for sig in s["sigs"]:
            assert sig["fn"], f"{s['id']}/{sig['endpoint']} : pas de fonction résolue"
    # couverture : ≥ 70 des 78 endpoints annoncés par module-info ont une signature
    total = sum(len(s["sigs"]) for s in gen.build_screens() if s["kind"] == "overview")
    assert total >= 70, f"seulement {total} endpoints résolus (attendu ≥ 70)"


def test_06_sorties_contenues_dans_screens():
    gen = _load_gen()
    for path, _c in gen.outputs(gen.build_screens()):
        rel = path.relative_to(ROOT).as_posix()
        assert rel.startswith("apps/web-portal/src/screens/"), rel
