"""Client MedGemma — analyse d'image contextualisée (premier avis)."""
from __future__ import annotations

import json

from tropirag.ai.model_client_base import ModelClientBase, load_prompt


class MedGemmaClient(ModelClientBase):
    """MedGemma-4B-IT : image + contexte clinique → observations structurées.

    N'est PAS diagnosticien. Fournit des observations descriptives qui
    alimentent le différentiel déterministe.
    """

    capability = "image_analysis"
    default_model_id = "medgemma-4b-it"
    temperature = 0.1
    max_tokens = 1024

    def analyze_image(self, image_b64: str, clinical_context: str,
                      language: str = "fr") -> "object":
        system = load_prompt("SYSTEM_PROMPT", "") or (
            "You are a medical image describer. Describe objectively. Never diagnose."
        )
        tpl = load_prompt("vision_analysis", "vision") or (
            "## CLINICAL CONTEXT\n{ctx}\n\nDescribe this image objectively: "
            "morphology, color, distribution, borders, extension. "
            "Output JSON: {\"description\": str, \"observations\": [str], "
            "\"concerning_features\": [str], \"context_elements\": [str]}"
        )
        prompt = tpl.format(ctx=clinical_context)
        resp = self._run(prompt, system=system, language=language,
                         images=[image_b64], json_mode=True)
        if resp.ok and resp.structured is None:
            try:
                resp.structured = json.loads(resp.text[resp.text.find("{"):resp.text.rfind("}") + 1])
            except (ValueError, json.JSONDecodeError):
                resp.structured = None
        return resp
