"""Chargeur HTML — extraction texte + repères de structure (stdlib pure).

Utilise ``html.parser`` : aucune dépendance tierce, aucun code exécuté,
script/style/noscript ignorés. Les titres h1-h6 sont conservés comme
marqueurs ``##`` pour alimenter le parseur de sections en aval.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

_BLOCK_TAGS = {
    "p", "div", "section", "article", "li", "ul", "ol", "table", "tr",
    "br", "hr", "header", "footer", "nav", "main", "aside", "figure",
}
_SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "head"}
_HEADING_TAGS = {"h1": "#", "h2": "#", "h3": "##", "h4": "###", "h5": "###", "h6": "###"}


class _HTMLTextExtractor(HTMLParser):
    """Collecte le texte visible avec repères de titres et sauts de blocs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0
        self._in_heading: str | None = None

    # -- gestionnaires ------------------------------------------------------
    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in _HEADING_TAGS:
            self._in_heading = _HEADING_TAGS[tag]
            self._chunks.append("\n")
        elif tag in _BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in _HEADING_TAGS:
            self._in_heading = None
            self._chunks.append("\n")
        elif tag in _BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth or not data.strip():
            return
        d = re.sub(r"\s+", " ", data)
        if self._in_heading and not self._chunks[-1:].count("\n") == 1:
            pass
        self._chunks.append(f"{self._in_heading} {d}\n" if self._in_heading else d)

    def handle_entityref(self, name: str) -> None:  # pragma: no cover
        self._chunks.append(f"&{name};")

    # -- résultat ------------------------------------------------------------
    def text(self) -> str:
        raw = "".join(self._chunks)
        # retire les lignes manifestement techniques (menus, pieds de page web)
        lines = [ln.strip() for ln in raw.splitlines()]
        return "\n".join(ln for ln in lines if ln)


def extract_html_text(html: str) -> str:
    """HTML → texte structuré (titres préfixés par des dièses)."""
    parser = _HTMLTextExtractor()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:  # HTML malformé : on garde ce qui est parsé
        if not parser.text():
            raise ValueError(f"HTML illisible : {exc}") from exc
    return parser.text()
