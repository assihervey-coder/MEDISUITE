"""Chargeur de documents — point d'entrée unique de l'ingestion.

Dispache par extension vers le loader adapté, calcule l'empreinte SHA-256
et conserve la piste d'audit (chemin, taille, date de collecte).
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path

from tropirag.evidence_engine.ingestion.html_loader import extract_html_text
from tropirag.evidence_engine.ingestion.pdf_loader import extract_pdf_text

SUPPORTED_EXTENSIONS = {".pdf", ".html", ".htm", ".txt", ".md", ".markdown"}


class LoadError(Exception):
    """Document illisible ou format non supporté."""


@dataclass(slots=True)
class RawDocument:
    """Document brut prêt pour la normalisation — piste d'audit incluse."""

    path: Path
    source_id: str                    # 'who-malaria-2023' (indice de nommage)
    content: str                      # texte extrait (non nettoyé)
    mime: str
    sha256: str
    size_bytes: int
    loaded_at: str
    extraction_mode: str = "internal"  # internal | pypdf
    warnings: list[str] = field(default_factory=list)

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()


class DocumentLoader:
    """Charge .pdf/.html/.htm/.txt/.md → RawDocument."""

    def load(self, path: Path | str, source_id: str | None = None) -> RawDocument:
        path = Path(path)
        if not path.exists():
            raise LoadError(f"fichier introuvable : {path}")
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise LoadError(
                f"extension non supportée '{path.suffix}' "
                f"(supportés : {', '.join(sorted(SUPPORTED_EXTENSIONS))})")
        data = path.read_bytes()
        if not data:
            raise LoadError(f"fichier vide : {path}")

        sid = source_id or self._guess_source_id(path)
        mime, text, mode, warnings = self._extract(path, data)

        return RawDocument(
            path=path, source_id=sid, content=text, mime=mime,
            sha256=hashlib.sha256(data).hexdigest(),
            size_bytes=len(data),
            loaded_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            extraction_mode=mode, warnings=warnings,
        )

    # ------------------------------------------------------------------
    def _extract(self, path: Path, data: bytes) -> tuple[str, str, str, list[str]]:
        ext = path.suffix.lower()
        warnings: list[str] = []
        if ext == ".pdf":
            from tropirag.evidence_engine.ingestion.pdf_loader import PDFLoadError
            try:
                text = extract_pdf_text(data)
            except PDFLoadError as exc:
                raise LoadError(f"PDF illisible ({path.name}) : {exc}") from exc
            mode = "pypdf" if _pypdf_available() else "internal"
            if not text.strip():
                warnings.append(
                    "aucune couche texte détectée — PDF probablement scanné ; "
                    "transcription OCR requise avant ingestion")
            return "application/pdf", text, mode, warnings
        if ext in (".html", ".htm"):
            try:
                html = data.decode("utf-8")
            except UnicodeDecodeError:
                html = data.decode("latin-1", errors="replace")
                warnings.append("encodage non-UTF-8 détecté — repli latin-1")
            return "text/html", extract_html_text(html), "internal", warnings
        # txt / md
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1", errors="replace")
            warnings.append("encodage non-UTF-8 détecté — repli latin-1")
        mime = "text/markdown" if ext in (".md", ".markdown") else "text/plain"
        return mime, text, "internal", warnings

    # ------------------------------------------------------------------
    @staticmethod
    def _guess_source_id(path: Path) -> str:
        """'who-paludisme-2023.md' → 'who-paludisme-2023'."""
        return path.stem

    def load_directory(self, directory: Path | str,
                       pattern: str = "**/*") -> list[RawDocument]:
        """Charge tous les documents supportés d'un dossier (récursif)."""
        directory = Path(directory)
        docs: list[RawDocument] = []
        for p in sorted(directory.glob(pattern)):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    docs.append(self.load(p))
                except LoadError:
                    continue  # les fichiers illisibles sont sautés silencieusement
        return docs


def _pypdf_available() -> bool:
    try:
        import pypdf  # noqa: F401
        return True
    except ImportError:
        return False
