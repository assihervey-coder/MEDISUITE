"""Chargeur PDF — extraction texte pur Python (zéro dépendance).

Stratégie :
1. Si ``pypdf`` est importable → usage prioritaire (extraction robuste).
2. Sinon → extracteur interne : décompression des flux FlateDecode puis
   lecture des opérateurs texte PDF (Tj, TJ, ') — suffisant pour les PDF
   texte simples (guidelines OMS/MSF exportés en PDF texte).

L'extracteur interne ne prétend PAS gérer les polices exotiques ni les
PDF scannés (image seule) : dans ce cas il renvoie un texte vide et le
pipeline place le document en quarantaine avec un diagnostic explicite.
"""
from __future__ import annotations

import re
import zlib


class PDFLoadError(Exception):
    """Échec d'extraction PDF (fichier corrompu ou sans couche texte)."""


def _try_pypdf(data: bytes) -> str | None:
    """Tente l'extraction via pypdf si la bibliothèque est disponible."""
    try:
        from pypdf import PdfReader  # type: ignore
        from io import BytesIO
    except ImportError:
        return None
    try:
        reader = PdfReader(BytesIO(data))
        pages: list[str] = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n\n".join(p for p in pages if p and p.strip())
    except Exception:  # pragma: no cover - pypdf échoue → fallback interne
        return None


# --- extracteur interne ------------------------------------------------------

_ESC = {  # séquences d'échappement des chaînes PDF
    b"\\(": b"(", b"\\)": b")", b"\\\\": b"\\",
    b"\\n": b"\n", b"\\r": b"\r", b"\\t": b"\t",
}


def _decode_pdf_string(raw: bytes) -> str:
    """Décode une chaîne PDF (parenthèses) en texte."""
    out = bytearray()
    i = 0
    while i < len(raw):
        if raw[i : i + 2] in _ESC:
            out += _ESC[raw[i : i + 2]]
            i += 2
            continue
        if raw[i : i + 3] == b"\\dd" or raw[i : i + 1] == b"\\":
            # échappement octal \ddd
            m = re.match(rb"\\([0-7]{1,3})", raw[i : i + 4])
            if m:
                out.append(int(m.group(1), 8) & 0xFF)
                i += len(m.group(0))
                continue
        out.append(raw[i])
        i += 1
    return out.decode("latin-1", errors="replace")


def _extract_text_from_stream(stream: bytes) -> str:
    """Extrait le texte d'un flux de contenu PDF."""
    text: list[str] = []
    # Tj : (chaîne) Tj   — TJ : [(a) -2 (b)] TJ   — ' : (chaîne) '
    for m in re.finditer(rb"\((?:[^()\\]|\\.|\([^()]*\))*\)\s*(?:Tj|')", stream):
        inner = m.group(0)
        inner = inner[1 : inner.rindex(b")")]
        text.append(_decode_pdf_string(inner))
    for m in re.finditer(rb"\[((?:[^\[\]])*?)\]\s*TJ", stream, re.DOTALL):
        array = m.group(1)
        parts = re.findall(rb"\((?:[^()\\]|\\.)*\)", array)
        text.append("".join(_decode_pdf_string(p[1:-1]) for p in parts))
    return "\n".join(t for t in text if t.strip())


def _decode_stream(data: bytes, filters: list[str]) -> bytes:
    for f in filters:
        if f in (b"FlateDecode", "/FlateDecode"):
            data = zlib.decompress(data)
        # les autres filtres (DCT, etc.) ne portent pas de texte
    return data


def extract_pdf_text(data: bytes, max_pages: int = 400) -> str:
    """Extraction texte : pypdf si dispo, sinon extracteur interne."""
    if not data.startswith(b"%PDF"):
        raise PDFLoadError("en-tête %PDF absent — fichier corrompu ou non-PDF")
    txt = _try_pypdf(data)
    if txt and txt.strip():
        return txt
    # --- interne : décompresser tous les flux, filtrer ceux qui portent du texte
    pages: list[str] = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.DOTALL):
        raw = m.group(1)
        try:
            decoded = _decode_stream(raw, [b"FlateDecode"])
        except zlib.error:
            continue
        if b"Tj" in decoded or b"TJ" in decoded:
            t = _extract_text_from_stream(decoded)
            if t.strip():
                pages.append(t)
        if len(pages) >= max_pages:
            break
    return "\n\n".join(pages)
