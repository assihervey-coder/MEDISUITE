"""Tests AI Mesh — capacités dynamiques, invariants, versions, adaptateurs."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tropirag.ai.registry import model_capabilities as caps_mod  # noqa: E402
from tropirag.ai.registry import model_versions as versions  # noqa: E402
from tropirag.ai.registry import model_metadata as meta_mod  # noqa: E402
from tropirag.ai.registry.model_registry import get_registry  # noqa: E402
from tropirag.ai.text.openbiollm.adapter import hedge, parse_synthesis  # noqa: E402
from tropirag.ai.text.deepseek_r1.adapter import parse_audit  # noqa: E402
from tropirag.ai.vision.medgemma.adapter import is_prescriptive, parse_vision  # noqa: E402


class TestModelCapabilitiesYaml:

    def test_yaml_charge_et_complet(self):
        caps = caps_mod.load_capabilities_yaml()
        assert len(caps) >= 9
        assert "med42-v2-70b" in caps
        med42 = caps["med42-v2-70b"]
        assert "clinical_reasoning" in med42["tasks"]
        assert med42["autonomous_diagnosis"] is False
        assert med42["evidence_required"] is True

    def test_invariants_ok_sur_tous(self):
        assert caps_mod.all_invariant_violations() == {}

    def test_invariant_autonomous_diagnosis_infranchissable(self):
        # même si quelqu'un falsifie le YAML, l'invariant est détecté
        viol = caps_mod.check_invariants("med42-v2-70b", {
            "tasks": ["clinical_reasoning"], "evidence_required": True,
            "autonomous_diagnosis": True})
        assert any("autonomous_diagnosis" in v for v in viol)

    def test_invariant_evidence_sur_synthese(self):
        viol = caps_mod.check_invariants("openbiollm-70b", {
            "tasks": ["biomedical_synthesis"], "evidence_required": False})
        assert any("evidence_required" in v for v in viol)

    def test_vision_sans_evidence_requise_conforme(self):
        # la vision produit des observations, pas des décisions → pas de
        # violation même sans evidence_required
        viol = caps_mod.check_invariants("medgemma-4b-it", {
            "tasks": ["image_analysis"], "evidence_required": False})
        assert viol == []

    def test_matrice_taches(self):
        matrix = caps_mod.tasks_matrix()
        assert matrix["clinical_reasoning"] == ["med42-v2-70b"]
        assert len(matrix["biomedical_synthesis"]) == 2
        assert set(matrix["image_analysis"]) >= {"medgemma-4b-it"}

    def test_fusion_registre_sans_derive(self):
        reg = get_registry()
        medgemma = reg.get("medgemma-4b-it")
        assert "fr" in medgemma.capabilities.languages  # V1.3 : en+fr
        # les capacités dynamiques par modèle suivent le registre
        from tropirag.ai.vision.medgemma.capabilities import capabilities
        assert capabilities()["languages"] == list(medgemma.capabilities.languages)


class TestModelVersions:

    def test_seed_10_modeles(self):
        assert len(versions.VERSIONS) >= 10
        v = versions.latest("med42-v2-70b")
        assert v is not None and v.model_id == "med42-v2-70b"

    def test_validation_gouvernance(self):
        versions.register_version(versions.ModelVersion(
            model_id="test-model", version="v9", sha256="abc",
            clinically_validated=False))
        out = versions.validate("test-model", "v9", "eval-hash-xyz",
                                validated_on="2026-09-12")
        assert out is not None and out.clinically_validated
        assert out.eval_set_hash == "eval-hash-xyz"
        assert out in versions.validated_versions()

    def test_version_inconnue(self):
        assert versions.get_version("inexistant", "v1") is None
        assert versions.validate("inexistant", "v1", "h") is None


class TestModelMetadata:

    def test_depuis_dict_complet(self):
        m = meta_mod.metadata_from_dict({
            "model_id": "test-x", "display_name": "Test X", "family": "text",
            "provider_gateway": "ollama", "vram_gb": 4, "priority": 30,
            "capabilities": {"tasks": ["logical_audit"], "languages": ["fr"],
                             "evidence_required": True}})
        assert m.capabilities.autonomous_diagnosis_allowed is False
        assert meta_mod.validate_metadata(m) == []

    def test_champs_manquants_rejetes(self):
        try:
            meta_mod.metadata_from_dict({"model_id": "x"})
            assert False, "devrait lever"
        except ValueError as e:
            assert "display_name" in str(e)

    def test_vram_incoherente_detectee(self):
        m = meta_mod.metadata_from_dict({
            "model_id": "big", "display_name": "Big", "family": "text",
            "provider_gateway": "ollama", "vram_gb": 4,
            "capabilities": {"min_vram_gb": 40}})
        assert any("min_vram" in v for v in meta_mod.validate_metadata(m))

    def test_resume_lisible(self):
        m = get_registry().get("bge-m3")
        s = meta_mod.summarize(m)
        assert "bge-m3" in s and "embeddings" in s


class TestAdaptersDefense:

    def test_openbiollm_hedging(self):
        text = "Ceci confirme le diagnostic certain de paludisme."
        out = hedge(text)
        assert "confirme" not in out and "certain" not in out

    def test_openbiollm_citations_dedupliquees(self):
        out = parse_synthesis({"synthesis": "ok", "themes": ["a"],
                               "citations": ["eu-1", "eu-1", "eu-2"]})
        assert out["citations"] == ["eu-1", "eu-2"]
        assert out["parse_ok"] is True

    def test_deepseek_coverage_borne(self):
        ok = parse_audit({"consistent": True, "coverage": 0.87})
        assert ok["coverage"] == 0.87 and ok["parse_ok"]
        bad = parse_audit({"consistent": True, "coverage": 7.3})
        assert bad["parse_ok"] is False and bad["coverage"] is None

    def test_medgemma_filtre_prescriptif(self):
        assert is_prescriptive("administrer 500 mg deux fois par jour")
        assert not is_prescriptive("éruption maculopapulaire diffuse sur le tronc")
        out = parse_vision({
            "description": "photo de peau",
            "observations": ["éruption pétéchiale diffuse",
                             "donner 1 g de paracétamol toutes les 6 heures"],
            "concerning_features": ["purpura extensif"],
            "context_elements": ["mollet droit"]})
        assert out["observations"] == ["éruption pétéchiale diffuse"]
        assert len(out["filtered"]) == 1
        assert all(not is_prescriptive(o) for o in out["concerning_features"])
