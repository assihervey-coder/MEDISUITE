"""Routes d'inférence du mesh (voix, vision, synthèse — sous garde)."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DictationRequest(BaseModel):
    audio_b64: str
    language: str = "fr"


class ImageRequest(BaseModel):
    image_b64: str
    clinical_context: str = ""
    language: str = "fr"


@router.get("/inference/nodes")
async def inference_nodes() -> dict:
    """Santé des nœuds Ollama du mesh (V1.1) — topologie réelle branchée.

    En mode déterministe : détaille les nœuds configurés via l'environnement
    (TROPIRAG_OLLAMA_NODES) sans exiger qu'ils soient joignables.
    """
    from tropirag.core.config import get_config
    from tropirag.ai.gateways.ollama_gateway import OllamaGateway

    cfg = get_config()
    gw = OllamaGateway.from_env(cfg.inference.ollama_url, timeout_s=3.0)
    report = gw.health()
    # modèles attendus par famille → commandes de pull manquantes
    from tropirag.ai.registry.model_registry import get_registry
    required = [m.model_id for m in get_registry().all()]
    missing = gw.missing_models(required) if cfg.inference.mode in ("ollama", "vllm") else {}
    return {**report,
            "inference_mode": cfg.inference.mode,
            "required_models": required,
            "missing_pulls": missing}


@router.post("/inference/dictate")
async def dictate(req: DictationRequest) -> dict:
    from tropirag.core.config import get_config

    from tropirag.ai.gateways.deterministic_gateway import DeterministicGateway
    from tropirag.ai.gateways.ollama_gateway import OllamaGateway
    from tropirag.ai.registry.model_registry import get_registry
    from tropirag.ai.routing.model_router import ModelRouter
    from tropirag.ai.speech.medasr.client import MedASRClient
    from tropirag.ai.gateways.inference_gateway import GatewayManager

    mode = get_config().inference.mode
    gws = [DeterministicGateway()]
    if mode == "ollama":
        gws.append(OllamaGateway.from_env(get_config().inference.ollama_url))
    mgr = GatewayManager(gws)
    client = MedASRClient(get_registry(), ModelRouter(get_registry(), mgr.health, mode), mgr)
    resp = client.transcribe(req.audio_b64, req.language)
    return {"ok": resp.ok, "text": resp.text if resp.ok else None,
            "model": resp.model_id, "error": resp.error}


@router.post("/inference/vision/analyze")
async def vision_analyze(req: ImageRequest) -> dict:
    from tropirag.ai.agents.vision_agent import VisionAgent
    from tropirag.core.config import get_config
    from tropirag.ai.gateways.deterministic_gateway import DeterministicGateway
    from tropirag.ai.gateways.ollama_gateway import OllamaGateway
    from tropirag.ai.gateways.inference_gateway import GatewayManager
    from tropirag.ai.registry.model_registry import get_registry
    from tropirag.ai.routing.model_router import ModelRouter

    mode = get_config().inference.mode
    gws = [DeterministicGateway()]
    if mode == "ollama":
        gws.append(OllamaGateway.from_env(get_config().inference.ollama_url))
    mgr = GatewayManager(gws)
    agent = VisionAgent().bind(ModelRouter(get_registry(), mgr.health, mode), mgr, get_registry())
    rep = agent.run(image_b64=req.image_b64, clinical_context=req.clinical_context,
                    language=req.language)
    return rep.to_dict()
