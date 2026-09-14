"""Task Router — mappe une étape clinique vers une capacité."""
from __future__ import annotations

from tropirag.core.enums import ClinicalTask
from tropirag.ai.routing.model_router import ModelRouter, RoutingDecision

STEP_TO_TASK = {
    "dictation": ClinicalTask.SPEECH_TO_TEXT_DICTATION,
    "conversation": ClinicalTask.SPEECH_TO_TEXT_CONVERSATION,
    "clinical_synthesis": ClinicalTask.CLINICAL_REASONING,
    "biomedical_synthesis": ClinicalTask.BIOMEDICAL_SYNTHESIS,
    "logical_audit": ClinicalTask.LOGICAL_AUDIT,
    "image_analysis": ClinicalTask.IMAGE_ANALYSIS,
    "image_triage": ClinicalTask.IMAGE_TRIAGE,
    "segmentation": ClinicalTask.IMAGE_SEGMENTATION,
    "embed": ClinicalTask.EMBEDDINGS,
    "rerank": ClinicalTask.RERANKING,
}


def route_step(step: str, router: ModelRouter, language: str = "fr") -> RoutingDecision:
    task = STEP_TO_TASK.get(step)
    if task is None:
        return RoutingDecision(ClinicalTask.CLINICAL_REASONING, None, [],
                               f"Étape inconnue: {step}", router.mode, degraded=True)
    return router.route(task, language=language)
