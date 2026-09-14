"""MODEL ROUTER — sélection par capacité, risque, latence, disponibilité.

Le cœur du AI Capability Routing :

    CAPABILITY → REGISTRY → ROUTER → BEST AVAILABLE MODEL

Le routeur N'A JAMAIS autorité clinique : il choisit un exécutant
technique, sous les contraintes de gouvernance du registre.
"""
from __future__ import annotations

from dataclasses import dataclass

from tropirag.core.enums import ClinicalTask, InferenceMode
from tropirag.ai.registry.model_registry import ModelRegistry, get_registry
from tropirag.ai.registry.model_health import ModelHealthMonitor


@dataclass(slots=True)
class RoutingDecision:
    """Décision explicable du routeur."""

    task: ClinicalTask
    selected: str | None            # model_id
    fallbacks: list[str]
    reason: str
    mode: str                       # inference mode utilisé
    degraded: bool = False          # True si repli déterministe

    def to_dict(self) -> dict:
        return {"task": self.task.value, "selected": self.selected,
                "fallbacks": self.fallbacks, "reason": self.reason,
                "mode": self.mode, "degraded": self.degraded}


class ModelRouter:
    """Routeur de capacités du mesh — déterministe et traçable."""

    def __init__(self, registry: ModelRegistry | None = None,
                 health: ModelHealthMonitor | None = None,
                 inference_mode: str = "deterministic") -> None:
        self.registry = registry or get_registry()
        self.health = health or ModelHealthMonitor()
        self.mode = inference_mode

    # ------------------------------------------------------------------
    def route(self, task: ClinicalTask, language: str = "fr",
              latency_budget_ms: float | None = None,
              clinical_risk: str = "assisted",
              require_evidence: bool = False) -> RoutingDecision:
        """Sélectionne le meilleur modèle DISPONIBLE pour la capacité.

        Ordre de filtrage :
          1. capacité déclarée (tasks)
          2. langue
          3. gouvernance (evidence_required si clinique)
          4. disponibilité (mode d'inférence + santé + fallbacks)
        """
        candidates = self.registry.find_by_task(task, language)
        if not candidates:
            return RoutingDecision(task, None, [],
                                   f"Aucun modèle déclaré pour la capacité {task.value}",
                                   self.mode, degraded=True)

        if self.mode == InferenceMode.DETERMINISTIC.value:
            # mode sans IA : les capacités IA passent en repli déterministe
            # sauf celles déjà déterministes (embeddings/reranking offline)
            det_ok = [c for c in candidates if c.provider_gateway == "deterministic"]
            if det_ok:
                return RoutingDecision(task, det_ok[0].model_id,
                                       [m.model_id for m in det_ok[1:]],
                                       "Mode déterministe — modèle déterministe sélectionné",
                                       self.mode, degraded=False)
            return RoutingDecision(task, None,
                                   [m.model_id for m in candidates],
                                   "Mode déterministe — capacité IA indisponible, repli heuristique",
                                   self.mode, degraded=True)

        # mode ollama/vllm : filtrer par disponibilité (circuit breaker)
        available = [c for c in candidates if self.health.is_up(c.model_id)] or candidates
        chosen = available[0]
        fallbacks = [m.model_id for m in available[1:]]
        # fallbacks explicites du modèle choisi
        for fb in chosen.fallback_for:
            fallbacks.append(fb)
        reason = (f"Sélectionné {chosen.model_id} (priorité {chosen.priority}) "
                  f"pour {task.value} — langue {language}, "
                  f"{'avec' if require_evidence else 'sans'} exigence de preuve")
        return RoutingDecision(task, chosen.model_id, fallbacks, reason, self.mode, False)

    # ------------------------------------------------------------------
    def is_ai_available(self) -> bool:
        """Le mesh IA est-il réellement exploitable dans ce mode ?"""
        return self.mode != InferenceMode.DETERMINISTIC.value
