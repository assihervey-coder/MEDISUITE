"""Client MedASR — dictée clinique."""
from __future__ import annotations

from tropirag.ai.model_client_base import ModelClientBase


class MedASRClient(ModelClientBase):
    """MedASR : voix du médecin → texte clinique structuré."""

    capability = "speech_dictation"
    default_model_id = "medasr-quantized"
    temperature = 0.0
    max_tokens = 0  # ASR : pas de génération libre

    def transcribe(self, audio_b64: str, language: str = "fr") -> "object":
        prompt = ("Medical dictation transcription. Output the verbatim text with "
                  "clinical terminology normalized (FR).")
        return self._run(prompt, audio=audio_b64, language=language)
