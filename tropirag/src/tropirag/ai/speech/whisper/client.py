"""Client Whisper — conversation multilingue / terrain."""
from __future__ import annotations

from tropirag.ai.model_client_base import ModelClientBase


class WhisperClient(ModelClientBase):
    """Whisper Large v3 : conversation complète, multilingue, code-switching."""

    capability = "conversation_transcription"
    default_model_id = "whisper-large-v3"
    temperature = 0.0

    def transcribe_conversation(self, audio_b64: str, language: str = "fr") -> "object":
        prompt = "Transcribe this clinical conversation verbatim, preserving languages."
        return self._run(prompt, audio=audio_b64, language=language)
