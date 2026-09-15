"""Tests du branchement réel Ollama (V1.1) — gateway multi-nœuds.

Un serveur HTTP mock simule Ollama : aucune carte graphique requise.
Vérifie : routage famille→nœud, repli réplique, messages pull, santé.
"""
from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from tropirag.ai.gateways.inference_gateway import InferenceRequest
from tropirag.ai.gateways.ollama_gateway import OllamaGateway


class _OllamaMock(BaseHTTPRequestHandler):
    """Simule /api/version, /api/tags et /api/generate d'un nœud Ollama."""

    # configuré par classe enfant : (models présents, réponse generate)
    MODELS: set[str] = set()
    GENERATE_TEXT: str = "OK CLINIQUE"
    REFUSE: bool = False

    def log_message(self, *a):  # silence
        pass

    def _json(self, obj, code=200):
        import json

        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/version":
            self._json({"version": "0.5.7-mock"})
        elif self.path == "/api/tags":
            self._json({"models": [{"name": m} for m in self.MODELS]})
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        import json

        if self.path == "/api/generate":
            if self.REFUSE:
                self._json({"error": "boom"}, 500)
                return
            length = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(length) or b"{}")
            model = str(req.get("model", ""))
            # comme Ollama réel : 404 si le modèle n'est pas présent sur ce nœud
            if not any(m == model or m.startswith(model) for m in self.MODELS):
                self._json({"error": f"model '{model}' not found, "
                                      f"try pulling it first"}, 404)
                return
            self._json({"response": self.GENERATE_TEXT,
                        "prompt_eval_count": 12, "eval_count": 8})
        else:
            self._json({"error": "not found"}, 404)


def _serve(handler_cls):
    srv = HTTPServer(("127.0.0.1", 0), handler_cls)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


@pytest.fixture()
def node_a():
    """Nœud 1 : familles légères."""
    class H(_OllamaMock):
        MODELS = {"whisper-large-v3:latest", "bge-m3:latest"}
    srv, url = _serve(H)
    yield url
    srv.shutdown()


@pytest.fixture()
def node_b():
    """Nœud 2 : textes lourds."""
    class H(_OllamaMock):
        MODELS = {"med42-v2-70b:latest", "openbiollm-70b:latest"}
    srv, url = _serve(H)
    yield url
    srv.shutdown()


@pytest.fixture()
def node_replica():
    """Nœud 3 : réplique texte."""
    class H(_OllamaMock):
        MODELS = {"med42-v2-70b:latest"}
    srv, url = _serve(H)
    yield url
    srv.shutdown()


# ---------------------------------------------------------------------------
# Routage par famille
# ---------------------------------------------------------------------------

class TestRoutageFamilles:
    def test_from_env_parse(self, node_a, node_b):
        import os

        os.environ["TROPIRAG_OLLAMA_NODES"] = (
            f"speech={node_a},vision={node_a},embeddings={node_a},"
            f"reranking={node_a},text={node_b},famille_inconnue=http://x:1"
        )
        try:
            gw = OllamaGateway.from_env()
            assert gw.family_urls["text"] == node_b
            assert gw.family_urls["speech"] == node_a
            assert "famille_inconnue" not in gw.family_urls
        finally:
            del os.environ["TROPIRAG_OLLAMA_NODES"]

    def test_modele_texte_route_vers_noeud_b(self, node_a, node_b):
        """Le registre déclare med42-v2-70b en famille text → nœud B."""
        gw = OllamaGateway(base_url=node_a, family_urls={"text": node_b})
        req = InferenceRequest(model_id="med42-v2-70b", task="synthesis",
                               prompt="Résume le cas")
        r = gw.infer(req)
        assert r.ok and r.text == "OK CLINIQUE"
        # disponible via sa famille (B) même si A est le défaut
        assert gw.is_available("med42-v2-70b")

    def test_disponibilite_par_famille(self, node_a, node_b):
        gw = OllamaGateway(base_url=node_b, family_urls={"speech": node_a})
        # whisper est sur node_a (famille speech), pas sur node_b (défaut)
        assert gw.is_available("whisper-large-v3")
        gw2 = OllamaGateway(base_url=node_b)
        assert not gw2.is_available("whisper-large-v3")

    def test_from_env_replicas(self, node_b, node_replica):
        """``replicas=URL|URL`` (et ``replica=`` répétable) alimentent le repli."""
        import os

        os.environ["TROPIRAG_OLLAMA_NODES"] = (
            f"text={node_b},replicas={node_replica}|http://node4.local:11434,"
            f"replica=http://node5.local:11434"
        )
        try:
            gw = OllamaGateway.from_env()
            assert gw.replica_urls == [node_replica, "http://node4.local:11434",
                                       "http://node5.local:11434"]
            assert gw.family_urls == {"text": node_b}
        finally:
            del os.environ["TROPIRAG_OLLAMA_NODES"]

    def test_from_env_replicas_sans_url_ignores(self):
        """Entrées vides / malformées : aucune réplique fantôme."""
        import os

        os.environ["TROPIRAG_OLLAMA_NODES"] = (
            "replicas=|  ,text=,speech=http://node1:11434"
        )
        try:
            gw = OllamaGateway.from_env()
            assert gw.replica_urls == []
            assert gw.family_urls == {"speech": "http://node1:11434"}
        finally:
            del os.environ["TROPIRAG_OLLAMA_NODES"]

    def test_topologie_complete_repli_sur_replica(self, node_a, node_replica):
        """Topologie nodes.yaml complète : text→node2 down → repli node3."""
        import os

        os.environ["TROPIRAG_OLLAMA_NODES"] = (
            f"speech={node_a},vision={node_a},embeddings={node_a},"
            f"reranking={node_a},text=http://127.0.0.1:9,"
            f"replicas={node_replica}"
        )
        try:
            gw = OllamaGateway.from_env(base_url=node_a)
            r = gw.infer(InferenceRequest(model_id="med42-v2-70b",
                                          task="synthesis", prompt="cas"))
            assert r.ok, f"repli réplique échoué : {r.error}"
            assert r.text == "OK CLINIQUE"
        finally:
            del os.environ["TROPIRAG_OLLAMA_NODES"]


# ---------------------------------------------------------------------------
# Répliques et repli
# ---------------------------------------------------------------------------

class TestRepli:
    def test_replique_si_noeud_principal_tombe(self, node_b):
        """Pas de serveur sur node_b_down → repli sur la réplique."""

        class H(_OllamaMock):
            MODELS = {"med42-v2-70b:latest"}
        srv, replica = _serve(H)
        try:
            gw = OllamaGateway(
                base_url="http://127.0.0.1:9",  # nœud principal injoignable
                family_urls={"text": "http://127.0.0.1:9"},
                replica_urls=[replica],
            )
            r = gw.infer(InferenceRequest(model_id="med42-v2-70b",
                                          task="synthesis", prompt="cas"))
            assert r.ok, f"repli échoué : {r.error}"
            assert r.text == "OK CLINIQUE"
        finally:
            srv.shutdown()

    def test_erreur_actionnable_si_modele_absent(self, node_a):
        gw = OllamaGateway(base_url=node_a)
        r = gw.infer(InferenceRequest(model_id="med42-v2-70b",
                                      task="synthesis", prompt="cas"))
        assert not r.ok
        assert "ollama pull" in (r.error or ""), r.error


# ---------------------------------------------------------------------------
# Santé et observabilité
# ---------------------------------------------------------------------------

class TestSante:
    def test_health_par_noeud(self, node_a, node_b, node_replica):
        gw = OllamaGateway(base_url=node_b, family_urls={"speech": node_a},
                           replica_urls=[node_replica])
        h = gw.health()
        assert set(h["nodes"]) == {node_a, node_b, node_replica}
        assert all(n["reachable"] for n in h["nodes"].values())
        assert h["nodes"][node_b]["models"] == 2
        assert h["nodes"][node_a]["models"] == 2
        assert h["nodes"][node_replica]["models"] == 1

    def test_missing_models(self, node_a):
        gw = OllamaGateway(base_url=node_a)
        missing = gw.missing_models(["whisper-large-v3", "med42-v2-70b"])
        assert "med42-v2-70b" in missing
        assert missing["med42-v2-70b"] == "ollama pull med42-v2-70b"
        assert "whisper-large-v3" not in missing


# ---------------------------------------------------------------------------
# Le pipeline ne casse jamais
# ---------------------------------------------------------------------------

class TestPipelineIntact:
    def test_repli_deterministe_pour_embeddings(self):
        """Ollama HS → les embeddings replient sur le déterministe (RAG intact)."""
        from tropirag.ai.gateways.deterministic_gateway import DeterministicGateway
        from tropirag.ai.gateways.inference_gateway import GatewayManager

        gw = OllamaGateway(base_url="http://127.0.0.1:9")
        mgr = GatewayManager([DeterministicGateway(), gw])
        r = mgr.execute(
            InferenceRequest(model_id="bge-m3", task="embeddings",
                            prompt="paludisme grossesse"),
            preferred="ollama",
        )
        assert r.ok  # servi par le déterministe
        assert r.gateway == "deterministic"

    def test_ia_hs_le_pipeline_clinique_survit(self):
        """Scénario E2E : l'IA est injoignable, l'analyse déterministe réussit quand même."""
        from tropirag.response_engine.response_orchestrator import process_case

        gw = OllamaGateway(base_url="http://127.0.0.1:9")  # injoignable
        from tropirag.ai.gateways.inference_gateway import GatewayManager
        from tropirag.ai.gateways.deterministic_gateway import DeterministicGateway
        from tropirag.ai.routing.model_router import ModelRouter
        from tropirag.ai.registry.model_registry import get_registry
        from tropirag.response_engine.response_orchestrator import ResponseOrchestrator

        orch = ResponseOrchestrator.__new__(ResponseOrchestrator)
        # reconstruire avec la gateway HS sans toucher à la config globale
        ResponseOrchestrator.__init__(
            orch, inference_mode="deterministic")
        # gateway HS injectée : le router doit l'écarter
        orch.gateway_manager = GatewayManager([DeterministicGateway(), gw])
        orch.router = ModelRouter(get_registry(), orch.gateway_manager.health,
                                  "deterministic")
        r = orch.process({
            "patient": {"age_years": 30},
            "free_text": "fièvre, frissons",
            "travel": {"segments": [{"country": "CI",
                                      "departure": "2026-08-30"}]},
        })
        assert r.urgency, "le pipeline doit toujours produire un verdict"
        assert r.citations, "le RAG déterministe doit citer"
