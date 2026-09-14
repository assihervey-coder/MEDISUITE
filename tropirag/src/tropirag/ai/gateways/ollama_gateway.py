"""Gateway Ollama — HTTP vers les serveurs Ollama du mesh (mono ou multi-nœuds).

Topologie supportée (V1.1 — branchement réel des nœuds) :

    OllamaGateway(base_url="http://localhost:11434")           # mono-nœud
    OllamaGateway.from_env()                                    # lit TROPIRAG_OLLAMA_NODES
    OllamaGateway(
        base_url="http://node1:11434",
        family_urls={                                            # routage par famille
            "speech":     "http://node1:11434",
            "vision":     "http://node1:11434",
            "embeddings": "http://node1:11434",
            "reranking": "http://node1:11434",
            "text":       "http://node2:11434",
        },
        replica_urls=["http://node3:11434"],                    # répliques croisées
    )

Variable d'environnement (format court) :

    TROPIRAG_OLLAMA_NODES=speech=http://node1:11434,vision=http://node1:11434,\
embeddings=http://node1:11434,reranking=http://node1:11434,text=http://node2:11434

Aucune IA ne décide ici : la gateway transporte, le registre contraint.
"""
from __future__ import annotations

import json
import os
import time

from tropirag.ai.gateways.inference_gateway import InferenceRequest, InferenceResponse

# familles reconnues dans le registre → clé de routage
_KNOWN_FAMILIES = ("speech", "vision", "text", "embeddings", "reranking", "segmentation")


class OllamaGateway:
    """Backend Ollama : /api/generate (chat + multimodal via Modelfile).

    Routage : modèle → famille (registre) → nœud. Si le modèle est inconnu,
    la passerelle teste la famille déclarée puis l'URL par défaut, puis les
    répliques — dans cet ordre déterministe.
    """

    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434",
                 timeout_s: float = 60.0,
                 family_urls: dict[str, str] | None = None,
                 replica_urls: list[str] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.family_urls = {k.rstrip("/"): v.rstrip("/") for k, v in (family_urls or {}).items()}
        self.replica_urls = [u.rstrip("/") for u in (replica_urls or [])]
        self._clients: dict[str, object] = {}  # url → httpx.Client paresseux

    # ------------------------------------------------------------------
    # Construction depuis l'environnement
    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls, base_url: str = "http://localhost:11434",
                timeout_s: float = 60.0) -> "OllamaGateway":
        """Construit la gateway en lisant TROPIRAG_OLLAMA_NODES.

        Format : famille=URL,famille=URL — les familles inconnues sont ignorées.
        """
        family_urls: dict[str, str] = {}
        spec = os.environ.get("TROPIRAG_OLLAMA_NODES", "")
        for part in spec.split(","):
            part = part.strip()
            if not part or "=" not in part:
                continue
            family, url = part.split("=", 1)
            family = family.strip().lower()
            if family in _KNOWN_FAMILIES and url.strip():
                family_urls[family] = url.strip()
        return cls(base_url=base_url, timeout_s=timeout_s, family_urls=family_urls)

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------
    def _get_client(self, url: str):
        import httpx

        if url not in self._clients:
            self._clients[url] = httpx.Client(timeout=self.timeout_s)
        return self._clients[url]

    def _model_family(self, model_id: str) -> str | None:
        """Famille déclarée dans le registre (jamais devinée par le nom)."""
        try:
            from tropirag.ai.registry.model_registry import get_registry

            model = get_registry().get(model_id)
            return model.family if model else None
        except Exception:  # noqa: BLE001 — le routage ne doit jamais échouer
            return None

    def _candidate_urls(self, model_id: str) -> list[str]:
        """URLs à essayer, ordre déterministe : famille → défaut → répliques."""
        urls: list[str] = []
        family = self._model_family(model_id)
        if family and family in self.family_urls:
            urls.append(self.family_urls[family])
        if self.base_url not in urls:
            urls.append(self.base_url)
        for u in self.replica_urls:
            if u not in urls:
                urls.append(u)
        return urls

    # ------------------------------------------------------------------
    # Disponibilité / santé
    # ------------------------------------------------------------------
    def _node_version(self, url: str) -> str | None:
        try:
            r = self._get_client(url).get(f"{url}/api/version", timeout=3.0)
            if r.status_code == 200:
                return str(r.json().get("version", "?"))
        except Exception:  # noqa: BLE001
            return None
        return None

    def _node_models(self, url: str) -> set[str]:
        try:
            r = self._get_client(url).get(f"{url}/api/tags", timeout=3.0)
            if r.status_code == 200:
                return {m.get("name", "") for m in r.json().get("models", [])}
        except Exception:  # noqa: BLE001
            return set()
        return set()

    def is_available(self, model_id: str) -> bool:
        """Le modèle est présent sur AU MOINS un nœud candidat."""
        for url in self._candidate_urls(model_id):
            models = self._node_models(url)
            if any(m.split(":")[0] == model_id or m.startswith(model_id) for m in models):
                return True
        return False

    def health(self) -> dict:
        """Santé par nœud : version Ollama + nombre de modèles + latence."""
        urls = {self.base_url}
        urls.update(self.family_urls.values())
        urls.update(self.replica_urls)
        nodes = {}
        for url in sorted(urls):
            t0 = time.perf_counter()
            version = self._node_version(url)
            latency = round((time.perf_counter() - t0) * 1000)
            models = self._node_models(url) if version else set()
            nodes[url] = {
                "reachable": version is not None,
                "version": version,
                "models": len(models),
                "latency_ms": latency,
            }
        return {
            "gateway": self.name,
            "default_url": self.base_url,
            "family_routing": self.family_urls,
            "replicas": self.replica_urls,
            "nodes": nodes,
        }

    def missing_models(self, required: list[str]) -> dict[str, str]:
        """Pour chaque modèle requis absent : la commande ollama pull à lancer."""
        out: dict[str, str] = {}
        for model_id in required:
            if not self.is_available(model_id):
                out[model_id] = f"ollama pull {model_id}"
        return out

    # ------------------------------------------------------------------
    # Inférence
    # ------------------------------------------------------------------
    def infer(self, request: InferenceRequest) -> InferenceResponse:  # noqa: C901
        t0 = time.perf_counter()
        payload: dict = {
            "model": request.model_id,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        if request.system:
            payload["system"] = request.system
        if request.images:
            payload["images"] = request.images  # base64 sans préfixe
        if request.audio:  # les modèles ASR Ollama acceptent la sortie texte directe
            payload["audio"] = request.audio
        if request.json_mode:
            payload["format"] = "json"

        last_error = "aucun nœud Ollama joignable"
        for url in self._candidate_urls(request.model_id):
            try:
                r = self._get_client(url).post(f"{url}/api/generate", json=payload,
                                               timeout=request.timeout_s)
                latency = (time.perf_counter() - t0) * 1000
                if r.status_code == 404 and "model" in r.text:
                    last_error = (f"Modèle '{request.model_id}' absent du nœud {url} — "
                                  f"lancer : ollama pull {request.model_id}")
                    continue
                if r.status_code != 200:
                    last_error = f"HTTP {r.status_code} ({url}): {r.text[:160]}"
                    continue
                data = r.json()
                text = str(data.get("response", "")).strip()
                structured = None
                if request.json_mode and text:
                    try:
                        structured = json.loads(text)
                    except json.JSONDecodeError:
                        structured = None
                return InferenceResponse(
                    model_id=request.model_id, text=text, structured=structured,
                    ok=bool(text), gateway=self.name, latency_ms=latency,
                    tokens_in=data.get("prompt_eval_count"),
                    tokens_out=data.get("eval_count"),
                )
            except Exception as e:  # noqa: BLE001 — essayer le nœud suivant
                last_error = f"{url}: {e}"
                continue
        return InferenceResponse(model_id=request.model_id, ok=False,
                                 gateway=self.name, error=last_error)
