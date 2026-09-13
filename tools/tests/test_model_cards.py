"""Tests des model-cards ×26 (chantier v0.10 — COUVERTURE-ARBRE-INITIAL §3).

Propriétés verrouillées :
1. DÉTERMINISME — deux générations successives sont identiques ;
2. IDEMPOTENCE DU DÉPÔT — les fiches committées == régénération (mode --check) ;
3. COMPLETUDE — 26 fiches + index, chaque fiche porte les sections normatives ;
4. ALIGNEMENT SOURCES — tâche/service/config de chaque fiche relus depuis
   datasets/registry.py et ai/multimodal/configs/*.yaml ;
5. HONNÊTETÉ — aucun chiffre de performance publié avant verrou M+18 :
   les métriques restent « 🔴 R6-R8 » dans TOUTES les fiches.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "tools" / "generate_model_cards.py"
OUT = ROOT / "compliance" / "mdr" / "model-cards"


def _load_gen():
    spec = importlib.util.spec_from_file_location("generate_model_cards", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_01_deterministic():
    gen = _load_gen()
    cards_a, _ = gen.build_cards()
    cards_b, _ = gen.build_cards()
    assert len(cards_a) == 26
    for a, b in zip(cards_a, cards_b):
        assert a["text"] == b["text"], a["slug"]


def test_02_committed_files_match_generation():
    gen = _load_gen()
    cards, modules = gen.build_cards()
    assert gen.check_out(OUT, cards, modules) == 0, (
        "les fiches committées dérivent de la régénération — "
        "relancer tools/generate_model_cards.py et recommittre")


def test_03_required_sections():
    gen = _load_gen()
    cards, _ = gen.build_cards()
    for c in cards:
        t = c["text"]
        for section in (
            f"# MC-{c['no']:02d} — ",
            "## 1. Usage prévu",
            "## 2. Hors champ",
            "## 3. Données",
            "## 4. Architecture et entraînement",
            "## 5. Performances — 🔴 à renseigner R6-R8",
            "## 6. Explicabilité",
            "## 7. Évaluation clinique et réglementaire",
            "## 8. Risques et biais",
            "## 9. Limites",
            "## 10. Supervision humaine",
            "## 11. Surveillance post-commercialisation",
            "## 12. Traçabilité",
        ):
            assert section in t, f"{c['slug']} : section absente {section!r}"


def test_04_alignment_with_sources():
    gen = _load_gen()
    modules, spec = gen._load_registry()
    cards, _ = gen.build_cards()
    by_slug = {c["slug"]: c for c in cards}
    for no, slug in modules:
        c = by_slug[slug]
        task = spec[slug]["label"]["task"]
        assert f"`{task}`" in c["text"], slug
        assert f"{no:02d}_{slug}.yaml" in c["text"], slug
        assert gen.MODULE_META[slug]["service"] in c["text"], slug
        # chaque variable discriminante du registre est citée dans la fiche
        for f in spec[slug]["discriminantes"]:
            assert f"`{f}`" in c["text"], f"{slug}: feature {f} absente"


def test_05_no_published_metrics_before_lock():
    gen = _load_gen()
    cards, _ = gen.build_cards()
    for c in cards:
        assert "AUCUN chiffre de performance" in c["text"], c["slug"]
        assert "🔴 R6-R8" in c["text"], c["slug"]
        assert "MEDISUITE-CI-01" in c["text"], c["slug"]
        assert "RM-01" in c["text"], c["slug"]


def test_06_index_covers_all_26():
    gen = _load_gen()
    cards, modules = gen.build_cards()
    idx = gen.render_index(cards, modules)
    for c in cards:
        assert c["file"] in idx
    assert "26 fiches couvrent" in idx
    # index écrit sur disque à jour
    disk = (OUT / "00-index-model-cards.md").read_text(encoding="utf-8")
    assert disk == idx, "index committé dérivé — régénérer"
