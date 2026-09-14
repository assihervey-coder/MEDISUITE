"""Erreurs et exceptions TropiRAG."""
from __future__ import annotations


class TropiRAGError(Exception):
    """Erreur de base avec code machine."""

    code = "E_TROPIRAG"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigError(TropiRAGError):
    code = "E_CONFIG"


class RuleLoadError(TropiRAGError):
    code = "E_RULE_LOAD"


class RuleEvaluationError(TropiRAGError):
    code = "E_RULE_EVAL"


class EvidenceUnavailableError(TropiRAGError):
    code = "E_EVIDENCE_UNAVAILABLE"


class SafetyViolationError(TropiRAGError):
    """Levée quand un invariant de sécurité absolu est violé (jamais attrapée silencieusement)."""

    code = "E_SAFETY_VIOLATION"


class ModelUnavailableError(TropiRAGError):
    code = "E_MODEL_UNAVAILABLE"


class ModelNotAuthorizedError(TropiRAGError):
    """Modèle non autorisé pour cette tâche (capacités insuffisantes)."""

    code = "E_MODEL_NOT_AUTHORIZED"


class GatewayTimeoutError(TropiRAGError):
    code = "E_GATEWAY_TIMEOUT"


class RetrievalError(TropiRAGError):
    code = "E_RETRIEVAL"


class PersistenceError(TropiRAGError):
    code = "E_PERSISTENCE"
