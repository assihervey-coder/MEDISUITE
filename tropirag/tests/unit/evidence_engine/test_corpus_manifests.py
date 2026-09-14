"""Tests des manifests d'intégrité et de la persistance d'index RAG."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from tropirag.core.config import CORPUS_DIR
from tropirag.evidence_engine.evidence_engine import EvidenceEngine
from scripts.build_integrity_manifest import generate, verify


class TestIntegrityManifest:

    def test_generation_et_verification(self, tmp_path, monkeypatch):
        # manifests écrits dans un bac à sable pour ne pas polluer le dépôt
        import scripts.build_integrity_manifest as mod
        monkeypatch.setattr(mod, "MANIFESTS", tmp_path)
        assert generate() == 0
        integrity = tmp_path / "integrity_manifest.yaml"
        assert integrity.exists()
        with open(integrity, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert data["units_total"] >= 40
        assert len(data["units"]) == data["units_total"]
        assert len(data["corpus_sha256"]) == 64
        # vérification OK
        assert verify(strict=True) == 0

    def test_tampon_detecte(self, tmp_path, monkeypatch):
        import scripts.build_integrity_manifest as mod
        monkeypatch.setattr(mod, "MANIFESTS", tmp_path)
        generate()
        # falsifie une unité
        units = sorted((CORPUS_DIR / "evidence_units").glob("eu-*.yaml"))[:1]
        original = units[0].read_bytes()
        try:
            units[0].write_bytes(original + b"\n# tampon\n")
            assert verify() == 1  # l'écart DOIT être détecté
        finally:
            units[0].write_bytes(original)  # restauration


class TestIndexPersistence:

    def test_save_load_index(self, tmp_path, monkeypatch):
        eng = EvidenceEngine()
        n = eng.load()
        assert n > 0
        # isole la persistance sur tmp_path
        monkeypatch.setattr(EvidenceEngine, "_index_dir",
                            lambda self: tmp_path)
        eng._save_indexes()
        meta = json.loads((tmp_path / "index_meta.json").read_text())
        assert meta["units"] == n

        # restauration : un second moteur charge les index sans reconstruire
        eng2 = EvidenceEngine()
        eng2.load()
        monkeypatch.setattr(EvidenceEngine, "_index_dir", lambda self: tmp_path)
        # _try_load_indexes doit réussir et servir les mêmes résultats
        assert eng2._try_load_indexes() is True or eng2._try_load_indexes() == True
        q = "paludisme sévère artésunate"
        pack_ref = eng.retrieve_evidence(q, top_k=5)
        pack_new = eng2.retrieve_evidence(q, top_k=5)
        assert [u.unit_id for u in pack_ref.units] == [u.unit_id for u in pack_new.units]

    def test_invalidation_sur_corpus_modifie(self, tmp_path, monkeypatch):
        eng = EvidenceEngine()
        eng.load()
        monkeypatch.setattr(EvidenceEngine, "_index_dir", lambda self: tmp_path)
        eng._save_indexes()
        # falsifie l'empreinte → restauration refusée
        meta_p = tmp_path / "index_meta.json"
        meta = json.loads(meta_p.read_text())
        meta["corpus_sha256"] = "0" * 64
        meta_p.write_text(json.dumps(meta))
        assert eng._try_load_indexes() is False
