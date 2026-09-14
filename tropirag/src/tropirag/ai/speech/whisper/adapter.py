"""Adapter Whisper."""
from __future__ import annotations


def parse_transcription(resp) -> dict:
    return {"text": resp.text if resp.ok else "", "ok": resp.ok,
            "model": resp.model_id, "multilingual": True}
