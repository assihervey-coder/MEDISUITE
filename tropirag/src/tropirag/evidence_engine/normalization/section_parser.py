"""Parseur de sections — découpe les directives cliniques en sections titrées.

Reconnaît trois familles de titres (par ordre de priorité) :
    1. Markdown : ``#``, ``##`` …
    2. Numéroté : ``1. Traitement``, ``3.2 Prise en charge``,
    3. Majuscules seules sur une ligne ou mots-clés métier connus
       (« Traitement », « Diagnostic », « Signes d'alarme » …).

Chaque section conserve son niveau et son chemin — c'est ce qui permet au
chunker clinique d'attacher le contexte à chaque extrait.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# mots-clés métier = titres de section même sans numérotation ni majuscules
_CLINICAL_SECTION_KEYWORDS = [
    "introduction", "contexte", "objectifs", "d[ée]finitions",
    "signes et sympt[ôo]mes", "sympt[ôo]mes", "pr[ée]sentation clinique",
    "diagnostic", "diagnostic diff[ée]rentiel", "examens compl[ée]mentaires",
    "biologie", "laboratoire", "traitement", "prise en charge",
    "signes d'alarme", "signes de gravit[ée]", "crit[èe]res de gravit[ée]",
    "surveillance", "pr[ée]vention", "vaccination", "prophylaxie",
    "notification", "d[ée]claration", "isolement", "r[ée]f[ée]rence",
    "escalade", "urgence", "complications", "populations particuli[èe]res",
    "grossesse", "enfant", "pharmacologie", "posologie", "contre-indications",
    "[ée]pid[ée]miologie", "surveillance [ée]pid[ée]miologique",
]

_MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)[.)]?\s+(\S.*)$")
_KW_HEADING = re.compile(
    r"^(" + "|".join(_CLINICAL_SECTION_KEYWORDS) + r")\b[:\s]*$",
    re.IGNORECASE,
)


@dataclass(slots=True)
class Section:
    """Section titrée d'un document clinique."""

    title: str
    level: int                  # 1 = chapitre, 2 = sous-section…
    path: list[str] = field(default_factory=list)   # hiérarchie des titres
    text: str = ""
    order: int = 0

    @property
    def full_title(self) -> str:
        return " > ".join(self.path) if self.path else self.title


class SectionParser:
    """Découpe un document nettoyé en sections titrées."""

    def parse(self, text: str, max_level: int = 3) -> list[Section]:
        sections: list[Section] = []
        stack: list[tuple[int, str]] = []       # (level, title)
        current: Section | None = None
        body: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            level, title = self._heading_level(line)
            if level is not None and level <= max_level and title:
                # flush de la section précédente
                if current is not None:
                    current.text = "\n".join(body).strip()
                    if current.text or current.title:
                        sections.append(current)
                # pile de hiérarchie
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, title))
                current = Section(title=title, level=level,
                                   path=[t for _, t in stack], order=len(sections))
                body = []
            else:
                body.append(raw_line)
        if current is not None:
            current.text = "\n".join(body).strip()
            if current.text or current.title:
                sections.append(current)

        # document sans aucun titre détecté → une seule section
        if not sections:
            sections = [Section(title="Document", level=1, path=["Document"],
                                text=text.strip(), order=0)]
        # sections vides (titres orphelins sans corps) supprimées
        return [s for s in sections if s.text or s.title]

    # ------------------------------------------------------------------
    def _heading_level(self, line: str) -> tuple[int | None, str]:
        s = line.strip()
        if not s:
            return None, ""
        m = _MD_HEADING.match(s)
        if m:
            return len(m.group(1)), m.group(2).strip()
        m = _NUMBERED.match(s)
        if m:
            # ne pas confondre avec une posologie en début de ligne
            title = m.group(2).strip()
            if len(title) >= 3 and not re.match(r"^\d", title):
                depth = m.group(1).count(".") + 1
                return depth, f"{m.group(1)} {title}"
        if _KW_HEADING.match(s):
            return 2, s.rstrip(":").strip()
        # ligne tout-en-majuscules, courte, sans point final → titre
        if (len(s) <= 70 and s == s.upper() and re.search(r"[A-ZÀ-Ý]{3}", s)
                and not s.endswith((".", ";", ",")) and not re.match(r"^[\d\s°-]+$", s)):
            return 2, s.title()
        return None, ""
