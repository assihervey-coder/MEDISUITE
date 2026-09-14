#!/usr/bin/env python3
"""Serveur Ollama simulé — TropiRAG.

Double usage :
  1. TESTS D'INTÉGRATION SANS GPU : la suite de tests et
     ``scripts/med42_xdr_synthesis_test.py --mock`` démarrent ce serveur en
     thread sur un port libre et pointent ``TROPIRAG_OLLAMA_NODES`` dessus —
     le branchement complet (gateway → routeur → agent Med42 → audit →
     Safety Gate) est alors exercé de bout en bout, sans aucun matériel.
  2. RÉPÉTITION GÉNÉRALE AVANT DÉPLOIEMENT : sur un poste quelconque,

         python scripts/mock_ollama_server.py --port 11434

     puis ``TROPIRAG_INFERENCE_MODE=ollama
     TROPIRAG_OLLAMA_NODES=text=http://127.0.0.1:11434`` — l'équipe valide la
     chaîne applicative AVANT que les nœuds GPU réels ne soient montés.

Le serveur reproduit l'API Ollama utilisée par TropiRAG :
  GET  /api/version   → version simulée
  GET  /api/tags      → modèles déclarés (registre TropiRAG par défaut)
  POST /api/generate  → réponse déterministe cliniquement plausible

⚠️ Les réponses sont DÉTERMINISTES et construites uniquement à partir du
prompt reçu (contexte + preuves citées). Ce mock ne « sait » rien : il
réorganise les preuves du prompt sous le format de sortie attendu —
exactement le comportement minimal qu'exigent les gardes de TropiRAG
(citations obligatoires, ancrage par unité, aucune posologie inventée).
Aucun contenu clinique n'est généré hors de ce qui est fourni.
"""
from __future__ import annotations

import argparse
import json
import re
import string
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Modèles du registre TropiRAG (noms réels Ollama, cf. deployment/ollama/)
DEFAULT_MODELS = [
    "med42-v2-70b:latest",
    "openbiollm-70b:latest",
    "deepseek-r1-distill-32b:latest",
    "medgemma-4b-it:latest",
    "minicpm-v-2.6:latest",
    "medasr-quantized:latest",
    "whisper-large-v3:latest",
    "bge-m3:latest",
    "qwen-reranker:latest",
]

_VERSION = "0.5.7-tropirag-mock"

# ---------------------------------------------------------------------------
# Générateur déterministe de synthèse (mode JSON — Med42 / OpenBioLLM)
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_UNIT_RE = re.compile(
    r"\[([a-z0-9][a-z0-9-]*)\]\s*\(([^)]*)\)\s*(.*?)(?=\n\n\[|\n\n##|\Z)",
    re.S,
)
# verbes neutralisés pour ne jamais déclencher le détecteur de contradictions
_VERB_SWAP = re.compile(r"\b(administrer|donner|prescrire|utiliser)\b", re.I)


def _neutralize(text: str) -> str:
    """Réécrit les verbes de prescription en verbe neutre (« envisager »)."""
    return _VERB_SWAP.sub("envisager", text)


def _first_sentences(text: str, n: int = 2, max_chars: int = 320) -> str:
    sents = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    out = " ".join(sents[:n])
    return out[:max_chars].rsplit(" ", 1)[0] if len(out) > max_chars else out


def build_synthesis(prompt: str) -> str:
    """Construit la réponse JSON de synthèse à partir du prompt Med42.

    Le prompt contient : ## CONTEXT, ## EVIDENCE ([eu-...] (source) texte),
    ## CONSTRAINTS. La sortie reprend uniquement le contenu des preuves,
    chaque phrase étant suffixée par sa citation d'unité.
    """
    def section(name: str) -> str:
        m = re.search(rf"##\s*{name}[^\n]*\n(.*?)(?=\n##\s|\Z)", prompt, re.S)
        return (m.group(1) if m else "").strip()

    context = section("CONTEXT")
    evidence = section("EVIDENCE")
    constraints_raw = section("CONSTRAINTS")

    units = _UNIT_RE.findall(evidence)
    unit_ids = [u[0] for u in units]

    findings: list[str] = []
    for uid, _src, text in units[:6]:
        sent = _first_sentences(text, n=2)
        if sent:
            findings.append(f"{_neutralize(sent)} [{uid}]")

    warnings = [_neutralize(line.lstrip("- ").strip())
                for line in constraints_raw.splitlines()
                if line.strip().startswith("-")]

    head = ("Synthèse de projet IA (à valider par le clinicien) — tableau fébrile "
            "suspecté compatible avec le contexte suivant : ")
    ctx = _neutralize(context.replace(" | ", " ; "))
    summary = head + ctx + ". Hypothèses à évoquer et conduites d'après les "
    "preuves citées ci-dessous, chaque affirmation ancrée dans son unité source. "
    if not findings:
        summary += "Aucune preuve exploitable fournie — synthèse impossible."
    else:
        summary += " ".join(findings)
    summary = summary[:4000]

    payload = {
        "summary": summary,
        "key_findings": findings,
        "differential_review": [
            "Révision du différentiel déterministe requise avant validation clinique."
        ],
        "warnings": (["Toute posologie reste de la responsabilité du clinicien "
                      "(jamais générée par l'IA)."] + warnings)[:8],
        "citations": unit_ids,
    }
    return json.dumps(payload, ensure_ascii=False)


def build_generic_text(payload: dict) -> str:
    """Réponses non-Med42 (ASR/vision/générique) — stubs déterministes."""
    model = str(payload.get("model", ""))
    if "whisper" in model or "medasr" in model:
        # transcription simulée : le « clinicien » dicte des symptômes
        return ("Patient vu en consultation, fièvre depuis trois jours, "
                "céphalées et douleurs musculaires, retour de voyage récent.")
    if "medgemma" in model or "minicpm" in model:
        return json.dumps({
            "triage": "image_non_conclusive",
            "note": "Mock vision : analyse d'image non disponible en simulation.",
        }, ensure_ascii=False)
    # texte générique : écho court et prudent
    return ("Réponse simulée — le mode mock ne produit pas de contenu clinique "
            "libre ; seules les synthèses sous contrat de preuves sont émises.")


# ---------------------------------------------------------------------------
# Serveur HTTP
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    """3 routes Ollama, réponses JSON déterministes, logs silencieux."""

    server_version = f"TropiRAGMock/{_VERSION}"

    def log_message(self, *args) -> None:  # silence complet (tests)
        return

    # -- helpers ------------------------------------------------------------
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _models(self) -> list[str]:
        return list(self.server.tropirag_models)  # type: ignore[attr-defined]

    # -- routes -------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api/version"):
            self._json(200, {"version": _VERSION})
        elif self.path.startswith("/api/tags"):
            self._json(200, {"models": [
                {"name": m, "model": m, "size": 1, "digest": m,
                 "modified_at": "2026-01-01T00:00:00Z", "details": {}}
                for m in self._models()]})
        else:
            self._json(404, {"error": f"route inconnue : {self.path}"})

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/api/generate"):
            self._json(404, {"error": f"route inconnue : {self.path}"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) or b"{}"
            payload = json.loads(raw)
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"error": "corps JSON invalide"})
            return
        self.server.calls.append({"path": self.path, "body": payload})  # type: ignore[attr-defined]

        model = str(payload.get("model", "")).split(":")[0]
        known = {m.split(":")[0] for m in self._models()}
        if model and model not in known:
            self._json(404, {"error": f"model '{model}' not found"})
            return

        wants_json = payload.get("format") == "json"
        is_text_family = any(k in model for k in ("med42", "openbiollm", "deepseek"))
        if wants_json and is_text_family:
            text = build_synthesis(str(payload.get("prompt", "")))
        else:
            text = build_generic_text(payload)

        self._json(200, {
            "model": model,
            "created_at": "2026-01-01T00:00:00Z",
            "response": text,
            "done": True,
            "done_reason": "stop",
            "context": [],
            "total_duration": 1_000_000,
            "load_duration": 1,
            "prompt_eval_count": 128,
            "eval_count": 96,
        })


class MockOllamaServer(ThreadingHTTPServer):
    """Serveur mock pilotable : modèles servis + compteur d'appels.

    ``start_background()`` écoute sur un port libre (choisi par l'OS) dans un
    thread daemon et retourne l'URL de base — usage typique des tests.
    """

    def __init__(self, models: list[str] | None = None, host: str = "127.0.0.1",
                 port: int = 0) -> None:
        super().__init__((host, port), _Handler)
        self.tropirag_models = list(models) if models else list(DEFAULT_MODELS)
        self.calls: list[dict] = []
        self.daemon_threads = True

    @property
    def url(self) -> str:
        return f"http://{self.server_address[0]}:{self.server_address[1]}"

    def start_background(self) -> str:
        """Démarre en thread daemon ; retourne l'URL de base."""
        t = threading.Thread(target=self.serve_forever, daemon=True)
        t.start()
        return self.url


# ---------------------------------------------------------------------------
# Mode autonome (répétition générale de déploiement)
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Serveur Ollama simulé TropiRAG")
    ap.add_argument("--port", type=int, default=11434,
                    help="port d'écoute (défaut 11434)")
    ap.add_argument("--models", default="",
                     help="liste de modèles simulés, séparés par des virgules "
                          "(défaut : registre TropiRAG complet)")
    args = ap.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()] or None
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        if probe.connect_ex(("127.0.0.1", args.port)) == 0:
            print(f"port {args.port} occupé — un Ollama réel y répond peut-être ; "
                  "utilisez --port différent")
            return 2
    srv = MockOllamaServer(models, port=args.port)
    print(f"Mock Ollama TropiRAG v{_VERSION} en écoute sur {srv.url}")
    print("Modèles servis :", ", ".join(srv.tropirag_models))
    print("Pointez le mesh : TROPIRAG_INFERENCE_MODE=ollama "
          f"TROPIRAG_OLLAMA_NODES=text={srv.url}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\narrêt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
