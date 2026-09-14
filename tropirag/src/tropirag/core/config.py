"""Configuration centrale TropiRAG — chargement YAML + variables d'environnement.

Toute la configuration est :
- déclarative (YAML sous configs/),
- surchargeable par variables d'environnement (TROPIRAG_*),
- validée par Pydantic,
- figée après premier chargement (singleton immuable).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Racines
# ---------------------------------------------------------------------------
TROPIRAG_ROOT = Path(
    os.environ.get("TROPIRAG_ROOT")
    or Path(__file__).resolve().parents[3]
)
if not (TROPIRAG_ROOT / "configs").exists():  # exécution depuis tests hors racine
    _cwd_candidate = Path.cwd()
    if (_cwd_candidate / "configs").exists():
        TROPIRAG_ROOT = _cwd_candidate

CONFIGS_DIR = TROPIRAG_ROOT / "configs"
CORPUS_DIR = TROPIRAG_ROOT / "corpus"
RULES_DIR = TROPIRAG_ROOT / "rules"
DATA_DIR = Path(os.environ.get("TROPIRAG_DATA_DIR") or TROPIRAG_ROOT)
RUNTIME_DIR = DATA_DIR / "runtime"
DB_PATH = Path(
    os.environ.get("TROPIRAG_DB_PATH")
    or (DATA_DIR / "db" / "tropirag.sqlite3")
)

# ---------------------------------------------------------------------------
# Sous-configs
# ---------------------------------------------------------------------------


class AppConfig(BaseModel):
    name: str = "tropirag"
    version: str = "0.1.0"
    environment: str = "local"
    jurisdiction_default: str = "CI"
    languages: list[str] = Field(default_factory=lambda: ["fr", "en"])
    timezone: str = "Africa/Abidjan"


class InferenceConfig(BaseModel):
    """Mode d'inférence du mesh IA."""

    mode: str = "deterministic"  # deterministic | ollama | vllm
    ollama_url: str = "http://localhost:11434"
    vllm_url: str = "http://localhost:8001"
    timeout_seconds: float = 60.0
    max_concurrent_requests: int = 8
    circuit_breaker_failures: int = 3
    circuit_breaker_reset_seconds: float = 300.0


class RetrievalConfig(BaseModel):
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    vector_dimensions: int = 256  # hashing déterministe offline
    vector_top_k: int = 30
    bm25_top_k: int = 30
    fusion_rrf_k: int = 60
    rerank_top_k: int = 5
    min_score: float = 0.01


class SecurityConfig(BaseModel):
    api_key: str = ""
    require_api_key: bool = True
    audit_enabled: bool = True
    pii_redact_in_logs: bool = True


class ObservabilityConfig(BaseModel):
    log_level: str = "INFO"
    log_format: str = "json"
    metrics_enabled: bool = True


class TropiRAGConfig(BaseModel):
    """Configuration racine agrégée."""

    app: AppConfig = Field(default_factory=AppConfig)
    inference: InferenceConfig = Field(default_factory=InferenceConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config() -> TropiRAGConfig:
    """Charge configs/**/*.yaml puis applique les surcharges d'environnement."""
    raw: dict[str, Any] = {}
    raw.update(_load_yaml(CONFIGS_DIR / "app" / "app.yaml"))

    ai_cfg = _load_yaml(CONFIGS_DIR / "ai" / "inference.yaml")
    rag_cfg = _load_yaml(CONFIGS_DIR / "rag" / "retrieval.yaml")
    sec_cfg = _load_yaml(CONFIGS_DIR / "security" / "security.yaml")
    obs_cfg = _load_yaml(CONFIGS_DIR / "observability" / "logging.yaml")

    env = os.environ.get("TROPIRAG_ENV", "local")
    env_over = _load_yaml(CONFIGS_DIR / "app" / "environments.yaml").get(env, {})
    raw = _deep_merge(raw, env_over)

    data: dict[str, Any] = {
        "app": raw.get("app", {}),
        "inference": ai_cfg.get("inference", {}),
        "retrieval": rag_cfg.get("retrieval", {}),
        "security": sec_cfg.get("security", {}),
        "observability": obs_cfg.get("logging", {}),
    }

    # --- surcharges environnementales -----------------------------------
    mode = os.environ.get("TROPIRAG_INFERENCE_MODE")
    if mode:
        data["inference"]["mode"] = mode
    if url := os.environ.get("TROPIRAG_OLLAMA_URL"):
        data["inference"]["ollama_url"] = url
    if url := os.environ.get("TROPIRAG_VLLM_URL"):
        data["inference"]["vllm_url"] = url
    if key := os.environ.get("TROPIRAG_API_KEY"):
        data["security"]["api_key"] = key
    if lvl := os.environ.get("TROPIRAG_LOG_LEVEL"):
        data["observability"]["log_level"] = lvl

    return TropiRAGConfig(**data)


@lru_cache(maxsize=1)
def get_config() -> TropiRAGConfig:
    """Configuration process-wide immuable après premier appel."""
    return load_config()
