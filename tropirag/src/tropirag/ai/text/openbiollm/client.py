"""Client OpenBioLLM — Biomedical Synthesizer (littérature, dossiers)."""
from __future__ import annotations

import json

from tropirag.ai.model_client_base import ModelClientBase, load_prompt


class OpenBioLLMClient(ModelClientBase):
    """OpenBioLLM-70B : synthèse biomédicale de littérature et dossiers complexes."""

    capability = "biomedical_synthesis"
    default_model_id = "openbiollm-70b"
    temperature = 0.2
    max_tokens = 3072

    def biomedical_synthesis(self, question: str, evidence_text: str,
                              language: str = "fr") -> "object":
        system = load_prompt("SYSTEM_PROMPT", "") or (
            "You are a biomedical literature synthesizer. Ground every claim in the "
            "provided evidence. No novel clinical recommendations. Output JSON."
        )
        prompt = (
            f"## QUESTION\n{question}\n\n## EVIDENCE\n{evidence_text}\n\n"
            "Produce JSON: {\"synthesis\": str, \"themes\": [str], \"gaps\": [str], "
            "\"citations\": [EU-id]}"
        )
        resp = self._run(prompt, system=system, language=language, json_mode=True)
        if resp.ok and resp.structured is None:
            try:
                resp.structured = json.loads(resp.text[resp.text.find("{"):resp.text.rfind("}") + 1])
            except (ValueError, json.JSONDecodeError):
                resp.structured = None
        return resp
