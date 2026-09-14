"""Chunker sémantique — découpe par phrases avec fusions et chevauchement.

Segmentation de phrases consciente des abréviations cliniques françaises
(« art. », « cf. », « q.s. », « env. »…) puis assemblage en blocs de taille
cible avec recouvrement, pour ne jamais couper une recommandation en deux.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# abréviations qui ne terminent PAS une phrase
_ABBREVIATIONS = (
    "art", "cf", "env", "etc", "ex", "fig", "inc", "max", "min", "nos",
    "pp", "qq", "qsp", "sq", "tab", "vs", "vol", "dr", "pr", "mé", "ed",
    "dip", "prof", "dept", "ann", "append", "annexe", "no", "réf", "ref",
)
_SPLIT_RE = re.compile(
    r"(?<=[.!?;])\s+(?=[A-ZÀ-Þ0-9«\"'(])"
)


class SemanticChunker:
    """Phrases → blocs de taille cible avec chevauchement."""

    def __init__(self, target_chars: int = 700, max_chars: int = 1100,
                 overlap_sentences: int = 1, min_chars: int = 120) -> None:
        self.target = target_chars
        self.max = max_chars
        self.overlap = overlap_sentences
        self.min = min_chars

    # ------------------------------------------------------------------
    def split_sentences(self, text: str) -> list[str]:
        sentences: list[str] = []
        for para in re.split(r"\n\s*\n", text):
            para = " ".join(para.split())
            if not para:
                continue
            parts = _SPLIT_RE.split(para)
            buf: list[str] = []
            for part in parts:
                buf.append(part)
                joined = " ".join(buf)
                # si la « phrase » se termine par une abréviation → continuer
                if self._ends_with_abbrev(joined):
                    continue
                sentences.append(joined.strip())
                buf = []
            if buf:
                rest = " ".join(buf).strip()
                if rest:
                    sentences.append(rest)
        return [s for s in sentences if s]

    def _ends_with_abbrev(self, sentence: str) -> bool:
        s = sentence.rstrip()
        if not s.endswith("."):
            return False
        stem = s[:-1].rstrip()
        words = stem.split()
        return bool(words) and words[-1].lower().strip(".") in _ABBREVIATIONS

    # ------------------------------------------------------------------
    def chunk(self, text: str) -> list[str]:
        """Texte → blocs ~target_chars, phrases entières uniquement."""
        sentences = self.split_sentences(text)
        if not sentences:
            return []
        chunks: list[str] = []
        current: list[str] = []
        size = 0
        for sentence in sentences:
            slen = len(sentence) + 1
            if size + slen > self.target and current:
                chunks.append(" ".join(current).strip())
                current = current[len(current) - self.overlap:] if self.overlap else []
                size = sum(len(s) + 1 for s in current)
            current.append(sentence)
            size += slen
            # garde-fou : phrase monstre → bloc seul
            if size >= self.max:
                chunks.append(" ".join(current).strip())
                current, size = [], 0
        if current:
            tail = " ".join(current).strip()
            if len(tail) < self.min and chunks:
                chunks[-1] = (chunks[-1] + " " + tail).strip()
            else:
                chunks.append(tail)
        return [c for c in chunks if len(c) >= max(self.min // 2, 30)]
