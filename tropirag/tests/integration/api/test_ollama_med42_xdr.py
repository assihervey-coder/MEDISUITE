"""Intégration Ollama → Med42 — synthèse encadrée sur les cas XDR (V1.3).

Exercice COMPLET de la chaîne IA en mode ollama, via un serveur mock embarqué
(zéro GPU requis) :

    gateway Ollama → routeur capacités → MedicalAgent (Med42)
    → audit déterministe → Safety Gate → réponse citée

Verrouillé par ces tests :
  T1  le routage français sélectionne bien med42-v2-70b (régression des
      langues déclarées — bug V1.3 corrigé) ;
  T2  cas modéré + question « XDR ? » → synthèse ai-validated, citée,
      auditable, sans diagnostic autonome ni posologie ;
  T3  cas XDR sévère → synthèse IA SUSPENDUE (invariant : cas grave =
      déterministe pur) ;
  T4  nœud injoignable → dégradation gracieuse en déterministe intégral ;
  T5  le prompt envoyé à Med42 contient bien le contexte ET les preuves
      (régression du template .format() — bug V1.3 corrigé).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mock_ollama_server import MockOllamaServer  # noqa: E402


@pytest.fixture()
def ollama_env(monkeypatch):
    """Démarre le mock Ollama et pointe le mesh dessus (mode ollama)."""
    srv = MockOllamaServer()
    url = srv.start_background()
    monkeypatch.setenv("TROPIRAG_INFERENCE_MODE", "ollama")
    monkeypatch.setenv("TROPIRAG_OLLAMA_NODES", f"text={url}")
    yield {"server": srv, "url": url}
    srv.shutdown()
    srv.server_close()


# ---------------------------------------------------------------------------
# Cas de référence
# ---------------------------------------------------------------------------

MODERATE_XDR_QUESTION = {
    "patient": {"age_years": 26},
    "free_text": "fièvre depuis 4 jours, douleurs abdominales, céphalées",
}

SEVERE_XDR_TRAVEL = {
    "patient": {"age_years": 28},
    "free_text": "fièvre depuis 8 jours, céphalées, douleurs abdominales, constipation",
    "vitals": {"temperature_c": 39.1},
}


class TestRoutageFrancais:
    def test_med42_routable_en_francais(self):
        """Le registre doit exposer Med42 pour clinical_reasoning en fr.

        Régression V1.3 : languages=['en'] excluait Med42 de TOUT le pipeline
        francophone — la synthèse IA était silencieusement impossible.
        """
        from tropirag.ai.registry.model_registry import get_registry
        from tropirag.core.enums import ClinicalTask

        found = [m.model_id for m in get_registry().find_by_task(
            ClinicalTask.CLINICAL_REASONING, "fr")]
        assert "med42-v2-70b" in found, (
            "med42-v2-70b doit être routable en français "
            f"(trouvés : {found}) — vérifier configs/ai/model_registry.yaml")


class TestPromptContrat:
    def test_prompt_contient_contexte_et_preuves(self):
        """Le template Med42 doit injecter le contexte et les preuves.

        Régression V1.3 : le prompt .md ne contenait AUCUN jeton d'injection
        et ses accolades JSON faisaient échouer str.format().
        """
        from tropirag.ai.model_client_base import load_prompt

        tpl = load_prompt("clinical_synthesis", "clinical")
        assert tpl, "prompt clinical_synthesis.md introuvable"
        assert "{{CONTEXT}}" in tpl and "{{EVIDENCE}}" in tpl \
            and "{{CONSTRAINTS}}" in tpl
        # les jetons remplacés ne subsistent pas dans le prompt final
        from tropirag.ai.text.med42.client import Med42Client
        # (test structurel : l'implémentation n'utilise plus tpl.format())
        import inspect

        src = inspect.getsource(Med42Client.clinical_synthesis)
        assert "tpl.format(" not in src
        assert '.replace("{{CONTEXT}}"' in src


class TestSyntheseMed42SurCasXDR:
    def test_cas_modere_synthese_ai_validee(self, ollama_env, days_ago):
        """Cas modéré + question clinicien XDR → Med42, citations, audit."""
        from tropirag.response_engine.response_orchestrator import (
            ResponseOrchestrator,
        )
        from tropirag.response_engine.response_validator import validate_response

        payload = dict(MODERATE_XDR_QUESTION)
        payload["travel"] = {"segments": [{"country": "CI",
                                           "departure": days_ago(30)}]}
        orch = ResponseOrchestrator(inference_mode="ollama")
        r = orch.process(payload,
                         user_question="faut-il craindre une souche XDR résistante ?")

        assert r.ai_layer == "ai-validated", (
            f"couche={r.ai_layer} — la synthèse IA devait être autorisée "
            f"(urgence={r.urgency}, sévérité={r.severity})")
        assert r.ai_synthesis, "synthèse IA absente"
        assert "[eu-cdc-typ-xdr-001]" in r.ai_synthesis, (
            "la synthèse doit citer la preuve XDR du pack")
        assert validate_response(r) == []
        # audit
        assert r.audit_summary["consistent"] is True
        assert r.audit_summary["coverage"] >= 0.8
        # exécutant
        trace = {s["step"]: s for s in r.provenance["trace"]}
        assert trace["ai_synthesis"]["model"] == "med42-v2-70b"
        # gardes
        low = r.ai_synthesis.lower()
        assert "diagnostic certain" not in low
        assert "diagnostic confirmé" not in low
        import re

        assert not re.search(r"\b\d+\s?(mg|µg|ml)\b", r.ai_synthesis)

    def test_cas_severe_synthese_suspendue(self, ollama_env, days_ago):
        """Retour de zone foyer XDR (sévère) → l'IA est suspendue."""
        from tropirag.response_engine.response_orchestrator import (
            ResponseOrchestrator,
        )

        payload = dict(SEVERE_XDR_TRAVEL)
        payload["travel"] = {"segments": [{"country": "PK",
                                           "departure": days_ago(35)}]}
        orch = ResponseOrchestrator(inference_mode="ollama")
        r = orch.process(payload)

        assert any("xdr" in f["code"] for f in r.red_flags)
        assert r.ai_layer == "deterministic", (
            "invariant violé : synthèse IA sur un cas sévère")
        assert r.ai_synthesis is None or r.ai_synthesis == ""
        assert r.red_flags and r.narrative, "la réponse déterministe reste complète"

    def test_noeud_injoignable_degradation_gracieuse(self, monkeypatch, days_ago):
        """Mesh IA absent → le pipeline déterministe prend le relais."""
        from tropirag.response_engine.response_orchestrator import process_case

        monkeypatch.setenv("TROPIRAG_INFERENCE_MODE", "ollama")
        monkeypatch.setenv("TROPIRAG_OLLAMA_NODES", "text=http://127.0.0.1:1")
        payload = dict(MODERATE_XDR_QUESTION)
        payload["travel"] = {"segments": [{"country": "CI",
                                           "departure": days_ago(30)}]}
        r = process_case(payload)
        assert r.ai_layer == "deterministic"
        assert r.narrative and r.matched_rule_ids
        assert r.citations, "les preuves restent servies sans IA"

    def test_mock_gateway_sante_et_modeles(self, ollama_env):
        """Le mock expose l'API Ollama attendue par la gateway."""
        from tropirag.ai.gateways.ollama_gateway import OllamaGateway

        gw = OllamaGateway.from_env()
        h = gw.health()
        node = h["nodes"][ollama_env["url"]]
        assert node["reachable"]
        assert node["version"] == "0.5.7-tropirag-mock"
        assert node["models"] >= 5
        assert gw.is_available("med42-v2-70b")
        assert not gw.is_available("modele-inconnu-xyz")
