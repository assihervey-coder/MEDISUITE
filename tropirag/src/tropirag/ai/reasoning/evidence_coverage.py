"""Couverture de preuve — part des messages critiques ancrés dans l'EvidencePack."""
from __future__ import annotations

import re


def coverage_score(text: str, required: list[str]) -> float:
    if not required:
        return 1.0
    low = text.lower()
    covered = 0
    for msg in required:
        kws = [w for w in re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ]{5,}", msg.lower())]
        if not kws or any(k in low for k in kws):
            covered += 1
    return covered / len(required)
