"""Nettoyeur de texte — hygiène typographique pour le RAG.

Opérations déterministes, sans perte d'information clinique :
    - unicodage des guillemets/tirets/espaces insécables,
    - recollage des mots coupés en fin de ligne (césure),
    - compression des espaces et lignes vides multiples,
    - suppression des en-têtes/pieds répétés (nombreux PDF),
    - normalisation des tirets de listes.
"""
from __future__ import annotations

import re
from collections import Counter

# correspondances typographiques → forme canonique
_CHAR_MAP = {
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\u00a0": " ", "\u202f": " ", "\u2009": " ", "\u200b": "",
    "\ufb01": "fi", "\ufb02": "fl",
    "\u0153": "oe", "\u0152": "OE",
}


class TextCleaner:
    """Nettoie le texte extrait sans altérer le contenu clinique."""

    def clean(self, text: str) -> str:
        t = text
        for src, dst in _CHAR_MAP.items():
            t = t.replace(src, dst)
        # recollage des césures : "palu-\ndisme" → "paludisme"
        t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
        # lignes : trim + compression des blancs horizontaux
        lines = [re.sub(r"[ \t]+", " ", ln.strip()) for ln in t.splitlines()]
        # suppression des lignes répétées ≥ 3 fois (en-têtes/pieds de page PDF)
        lines = self._drop_repeated(lines)
        # compression des lignes vides multiples
        out: list[str] = []
        blank = 0
        for ln in lines:
            if not ln:
                blank += 1
                if blank <= 1:
                    out.append("")
            else:
                blank = 0
                out.append(ln)
        # puces canoniques
        result = "\n".join(out).strip()
        result = re.sub(r"^[•·▪●‣]\s*", "- ", result, flags=re.MULTILINE)
        result = re.sub(r"^[\u2023\u2043]\s*", "- ", result, flags=re.MULTILINE)
        return result

    # ------------------------------------------------------------------
    @staticmethod
    def _drop_repeated(lines: list[str], threshold: int = 3,
                       min_len: int = 6) -> list[str]:
        """Retire les lignes identiques répétées (pagination, filigranes)."""
        counts = Counter(ln for ln in lines if len(ln) >= min_len)
        repeated = {ln for ln, n in counts.items() if n >= threshold}
        if not repeated:
            return lines
        return [ln for ln in lines if ln not in repeated]
