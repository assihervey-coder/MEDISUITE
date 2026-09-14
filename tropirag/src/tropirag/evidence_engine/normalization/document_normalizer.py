"""Normalisateur de document — orchestre nettoyage + sections + terminologie.

Produit un ``NormalizedDocument`` : texte propre, sections titrées, métadonnées
inférées, annotations terminologiques par section. C'est l'entrée directe du
chunker clinique.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from tropirag.evidence_engine.ingestion.document_loader import RawDocument
from tropirag.evidence_engine.ingestion.metadata_extractor import (
    ExtractedMetadata,
    MetadataExtractor,
)
from tropirag.evidence_engine.normalization.section_parser import Section, SectionParser
from tropirag.evidence_engine.normalization.terminology_mapper import (
    TermMapping,
    TerminologyMapper,
)
from tropirag.evidence_engine.normalization.text_cleaner import TextCleaner


@dataclass(slots=True)
class AnnotatedSection:
    """Section + annotations terminologiques."""

    section: Section
    terms: TermMapping = field(default_factory=TermMapping)


@dataclass(slots=True)
class NormalizedDocument:
    """Document prêt pour le chunking clinique."""

    source_id: str
    content: str                       # texte nettoyé complet
    sections: list[AnnotatedSection] = field(default_factory=list)
    metadata: ExtractedMetadata = field(default_factory=ExtractedMetadata)
    sha256: str = ""
    path: str = ""
    warnings: list[str] = field(default_factory=list)

    def sections_with_terms(self) -> list[AnnotatedSection]:
        return [s for s in self.sections if s.terms.total > 0]

    def all_disease_codes(self) -> list[str]:
        out: set[str] = set()
        for s in self.sections:
            out |= set(s.terms.disease_codes)
        return sorted(out)

    def word_count(self) -> int:
        return len(re.findall(r"\S+", self.content))


class DocumentNormalizer:
    """Texte brut → document normalisé annoté."""

    def __init__(self) -> None:
        self._cleaner = TextCleaner()
        self._parser = SectionParser()
        self._mapper = TerminologyMapper()
        self._metadata = MetadataExtractor()

    def normalize(self, raw: RawDocument, metadata: ExtractedMetadata | None = None) -> NormalizedDocument:
        cleaned = self._cleaner.clean(raw.content)
        meta = metadata or self._metadata.extract(cleaned, source_id=raw.source_id)
        sections = self._parser.parse(cleaned)
        annotated: list[AnnotatedSection] = []
        for sec in sections:
            annotated.append(AnnotatedSection(section=sec, terms=self._mapper.map_text(sec.text)))
        return NormalizedDocument(
            source_id=raw.source_id, content=cleaned, sections=annotated,
            metadata=meta, sha256=raw.sha256, path=str(raw.path),
            warnings=list(raw.warnings),
        )
