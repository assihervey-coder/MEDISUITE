"""Adapter segmentation."""
from __future__ import annotations

from typing import Any


def parse_segmentation(structured: Any) -> dict:
    if not isinstance(structured, dict):
        return {"mask_available": False, "area_fraction": None,
                "bounding_box": [], "measurements": "", "parse_ok": False}
    return {"mask_available": bool(structured.get("mask_available", False)),
            "area_fraction": structured.get("area_fraction"),
            "bounding_box": list(structured.get("bounding_box", [])),
            "measurements": str(structured.get("measurements", "")),
            "parse_ok": True}
