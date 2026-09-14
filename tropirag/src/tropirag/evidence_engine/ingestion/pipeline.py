"""Pipeline d'ingestion documentaire — document brut → unités de preuve en quarantaine.

Étapes strictement déterministes et auditées :
    1. chargement (PDF/HTML/TXT/MD) + empreinte SHA-256,
    2. extraction des métadonnées,
    3. normalisation (nettoyage + sections + terminologie),
    4. chunking clinique,
    5. validation des chunks,
    6. génération d'unités de preuve DRAFT dans ``corpus/quarantine/``,
    7. (validation humaine) → promotion vers ``corpus/evidence_units/``.

AUCUNE unité issue du pipeline n'entre dans le corpus actif sans validation
humaine explicite — c'est le cycle de vie EVIDENCE_LIFECYCLE.md.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tropirag.core.config import CORPUS_DIR
from tropirag.evidence_engine.chunking.chunk_validator import ChunkValidator
from tropirag.evidence_engine.chunking.clinical_chunker import ClinicalChunker
from tropirag.evidence_engine.ingestion.document_loader import (
    DocumentLoader,
    LoadError,
    RawDocument,
)
from tropirag.evidence_engine.ingestion.metadata_extractor import ExtractedMetadata
from tropirag.evidence_engine.normalization.document_normalizer import DocumentNormalizer

_QUARANTINE_DIR = CORPUS_DIR / "quarantine"


@dataclass(slots=True)
class IngestionReport:
    """Rapport d'ingestion d'un document — pièce d'audit."""

    source_id: str
    path: str
    sha256: str = ""
    status: str = "draft"                 # draft | rejected | error
    units_created: int = 0
    chunks_valid: int = 0
    chunks_rejected: int = 0
    metadata: ExtractedMetadata = field(default_factory=ExtractedMetadata)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    unit_files: list[str] = field(default_factory=list)
    ingested_at: str = ""

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id, "path": self.path, "sha256": self.sha256,
            "status": self.status, "units_created": self.units_created,
            "chunks_valid": self.chunks_valid, "chunks_rejected": self.chunks_rejected,
            "metadata": self.metadata.as_source_dict(),
            "warnings": self.warnings, "errors": self.errors,
            "unit_files": self.unit_files, "ingested_at": self.ingested_at,
        }


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:40] or "doc"


class DocumentIngestionPipeline:
    """Document → chunks validés → unités de preuve DRAFT (quarantaine)."""

    def __init__(self, quarantine_dir: Path | None = None) -> None:
        self.loader = DocumentLoader()
        self.normalizer = DocumentNormalizer()
        self.chunker = ClinicalChunker()
        self.validator = ChunkValidator()
        self.quarantine_dir = Path(quarantine_dir or _QUARANTINE_DIR)

    # ------------------------------------------------------------------
    def ingest(self, path: Path | str, source_id: str | None = None) -> IngestionReport:
        report = IngestionReport(source_id="", path=str(path),
                                  ingested_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
        try:
            raw = self.loader.load(path, source_id=source_id)
        except LoadError as exc:
            report.status = "error"
            report.errors.append(str(exc))
            return report

        report.source_id = raw.source_id
        report.sha256 = raw.sha256
        report.warnings.extend(raw.warnings)

        if not raw.content.strip():
            report.status = "rejected"
            report.errors.append("aucun texte extrait — document ignoré (OCR requis ?)")
            return report

        normalized = self.normalizer.normalize(raw)
        report.metadata = normalized.metadata
        if normalized.metadata.authority == "unknown":
            report.warnings.append(
                "autorité non identifiée — validation humaine obligatoire avant promotion")

        chunks = self.chunker.chunk_document(normalized)
        validation = self.validator.validate(chunks)
        report.chunks_valid = len(validation.valid)
        report.chunks_rejected = len(validation.rejected)

        if not validation.valid:
            report.status = "rejected"
            report.errors.append(
                "aucun chunk valide — signal clinique insuffisant")
            return report

        # --- génération des unités DRAFT en quarantaine --------------------
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        slug = _slug(normalized.source_id)
        prefix = f"eu-draft-{slug}"
        for chunk in validation.valid:
            unit_id = f"{prefix}-{chunk.chunk_index + 1:03d}"
            payload = chunk.to_evidence_unit_dict(unit_id)
            payload["status"] = "draft"
            payload["provenance"] = {
                "pipeline": "tropirag-ingestion-v1",
                "source_sha256": raw.sha256,
                "source_path": str(raw.path),
                "extracted_at": raw.loaded_at,
                "extraction_mode": raw.extraction_mode,
            }
            fname = self.quarantine_dir / f"{unit_id}.yaml"
            with open(fname, "w", encoding="utf-8") as fh:
                yaml.safe_dump(payload, fh, allow_unicode=True, sort_keys=False)
            report.unit_files.append(str(fname))
            report.units_created += 1
        report.status = "draft"
        return report

    # ------------------------------------------------------------------
    def ingest_directory(self, directory: Path | str) -> list[IngestionReport]:
        return [self.ingest(p) for p in sorted(Path(directory).rglob("*"))
                if p.is_file() and p.suffix.lower() in
                {".pdf", ".html", ".htm", ".txt", ".md", ".markdown"}]

    # ------------------------------------------------------------------
    @staticmethod
    def promote(unit_file: Path | str, authority: str | None = None,
                edition_date: str | None = None) -> Path:
        """PROMOTION : quarantaine → corpus actif (décision humaine explicite).

        Le fichier est déplacé vers ``corpus/evidence_units/`` et son statut
        passe de ``draft`` à ``active``. La traçabilité d'origine est conservée.
        """
        unit_file = Path(unit_file)
        with open(unit_file, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        data["status"] = "active"
        data["promoted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        if authority:
            data["validated_authority"] = authority
        if edition_date:
            data["validated_edition_date"] = edition_date
        target = CORPUS_DIR / "evidence_units" / unit_file.name
        with open(target, "w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)
        unit_file.unlink(missing_ok=True)
        return target
