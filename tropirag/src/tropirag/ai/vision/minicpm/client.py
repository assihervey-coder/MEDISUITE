"""Client MiniCPM-V — triage image / screening."""
from __future__ import annotations

import json

from tropirag.ai.model_client_base import ModelClientBase


class MiniCPMClient(ModelClientBase):
    """MiniCPM-V 2.6 : screening rapide — sensibilité/spécificité équilibrées."""

    capability = "image_triage"
    default_model_id = "minicpm-v-2.6"
    temperature = 0.0
    max_tokens = 512

    def triage_image(self, image_b64: str, language: str = "fr") -> "object":
        prompt = (
            "Screening triage of this image. Output JSON: "
            "{\"flag\": \"normal|abnormal|urgent\", \"confidence\": 0-1, "
            "\"reason\": str, \"recommended_action\": str}"
        )
        resp = self._run(prompt, images=[image_b64], language=language, json_mode=True)
        if resp.ok and resp.structured is None:
            try:
                resp.structured = json.loads(resp.text[resp.text.find("{"):resp.text.rfind("}") + 1])
            except (ValueError, json.JSONDecodeError):
                resp.structured = None
        return resp
