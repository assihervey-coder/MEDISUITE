"""Client segmentation — masques et mesures."""
from __future__ import annotations

from tropirag.ai.model_client_base import ModelClientBase


class SegmentationClient(ModelClientBase):
    """Segmentation (VoxTell/MedFuse-Seg/SAM2) : lésion → masque → mesures."""

    capability = "image_segmentation"
    default_model_id = "sam2-medical"
    temperature = 0.0
    max_tokens = 256

    def segment(self, image_b64: str, language: str = "fr") -> "object":
        prompt = ("Segment the lesion. Output JSON: {\"mask_available\": bool, "
                  "\"area_fraction\": 0-1, \"bounding_box\": [x,y,w,h], \"measurements\": str}")
        return self._run(prompt, images=[image_b64], language=language, json_mode=True)
