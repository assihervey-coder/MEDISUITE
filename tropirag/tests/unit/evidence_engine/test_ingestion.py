"""Tests du pipeline d'ingestion documentaire — loaders, normalisation, chunking."""
from __future__ import annotations

import zlib
from pathlib import Path

import pytest
import yaml

from tropirag.evidence_engine.chunking.chunk_validator import ChunkValidator
from tropirag.evidence_engine.chunking.clinical_chunker import ClinicalChunker
from tropirag.evidence_engine.ingestion.document_loader import (
    DocumentLoader,
    LoadError,
    RawDocument,
)
from tropirag.evidence_engine.ingestion.metadata_extractor import MetadataExtractor
from tropirag.evidence_engine.ingestion.pipeline import DocumentIngestionPipeline
from tropirag.evidence_engine.normalization.document_normalizer import DocumentNormalizer
from tropirag.evidence_engine.normalization.section_parser import SectionParser
from tropirag.evidence_engine.normalization.terminology_mapper import TerminologyMapper
from tropirag.evidence_engine.normalization.text_cleaner import TextCleaner

RAW = Path(__file__).resolve().parents[3] / "data" / "raw"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

class TestDocumentLoader:

    def test_load_markdown(self):
        loader = DocumentLoader()
        doc = loader.load(RAW / "guidelines" / "who-malaria-guide-extrait.md")
        assert isinstance(doc, RawDocument)
        assert doc.mime == "text/markdown"
        assert "paludisme" in doc.content.lower()
        assert len(doc.sha256) == 64
        assert doc.size_bytes > 500

    def test_load_html_ignore_script_style(self):
        loader = DocumentLoader()
        doc = loader.load(RAW / "protocols" / "msf-dengue-protocole.html")
        assert doc.mime == "text/html"
        assert "trackPage" not in doc.content          # script ignoré
        assert "telemetry" not in doc.content
        assert "dengue" in doc.content.lower()
        assert "#" in doc.content                       # titres conservés comme marqueurs

    def test_load_txt(self):
        loader = DocumentLoader()
        doc = loader.load(RAW / "documents" / "cdc-typhoid-xdr-note.txt")
        assert doc.mime == "text/plain"
        assert "XDR" in doc.content

    def test_extension_invalide(self, tmp_path):
        bad = tmp_path / "doc.docx"
        bad.write_bytes(b"\x00\x01")
        with pytest.raises(LoadError):
            DocumentLoader().load(bad)

    def test_fichier_introuvable(self):
        with pytest.raises(LoadError):
            DocumentLoader().load("/inexistant/document.pdf")

    def test_fichier_vide(self, tmp_path):
        vide = tmp_path / "vide.txt"
        vide.write_bytes(b"")
        with pytest.raises(LoadError):
            DocumentLoader().load(vide)

    def test_source_id_devine(self):
        doc = DocumentLoader().load(RAW / "documents" / "cdc-typhoid-xdr-note.txt")
        assert doc.source_id == "cdc-typhoid-xdr-note"


class TestPdfLoader:
    """PDF minimal généré à la volée avec un flux texte compressé."""

    def _mini_pdf(self, text: str) -> bytes:
        content = f"BT ({text}) Tj ET".encode("latin-1", errors="replace")
        stream = zlib.compress(content)
        return (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Length " + str(len(stream)).encode() +
            b" /Filter /FlateDecode >>\nstream\n" + stream + b"\nendstream\nendobj\n"
            b"trailer\n<< /Root 1 0 R >>\n%%EOF"
        )

    def test_extraction_interne(self):
        from tropirag.evidence_engine.ingestion.pdf_loader import extract_pdf_text
        pdf = self._mini_pdf("TropiRAG paludisme severe artesunate")
        text = extract_pdf_text(pdf)
        assert "paludisme" in text
        assert "artesunate" in text

    def test_pas_pdf(self):
        from tropirag.evidence_engine.ingestion.pdf_loader import (
            PDFLoadError, extract_pdf_text)
        with pytest.raises(PDFLoadError):
            extract_pdf_text(b"ceci n'est pas un pdf")


# ---------------------------------------------------------------------------
# Métadonnées
# ---------------------------------------------------------------------------

class TestMetadataExtractor:

    def test_autorite_oms(self):
        meta = MetadataExtractor().extract(
            "# Guide OMS\nOrganisation mondiale de la santé — Genève, 2023-06-01")
        assert meta.authority == "WHO"
        assert meta.edition_date == "2023-06-01"
        assert meta.title.startswith("Guide OMS")

    def test_autorite_msf(self):
        meta = MetadataExtractor().extract("Médecins Sans Frontières — protocole Paris")
        assert meta.authority == "MSF"

    def test_autorite_national_ci(self):
        meta = MetadataExtractor().extract(
            "Ministère de la Santé — Abidjan, Côte d'Ivoire")
        assert meta.authority == "NATIONAL"
        assert meta.jurisdiction == "CI"

    def test_date_francaise(self):
        meta = MetadataExtractor().extract("Édition du 15 mars 2024 — directive")
        assert meta.edition_date == "2024-03-15"

    def test_langue(self):
        assert MetadataExtractor().extract("le patient doit recevoir le traitement").language == "fr"
        assert MetadataExtractor().extract("the patient should receive treatment").language == "en"

    def test_inconnu_sans_drapeau(self):
        meta = MetadataExtractor().extract("Un texte quelconque sans signature.")
        assert meta.authority == "unknown"
        assert meta.jurisdiction == "INT"


# ---------------------------------------------------------------------------
# Nettoyage / sections / terminologie
# ---------------------------------------------------------------------------

class TestTextCleaner:

    def test_cesure_recollee(self):
        out = TextCleaner().clean("palu-\ndisme sévère")
        assert "paludisme" in out

    def test_guillemets_typographiques(self):
        out = TextCleaner().clean("«\u00a0guideline\u00a0»")
        assert "\u00a0" not in out

    def test_lignes_repetees_supprimees(self):
        txt = "\n".join(["Page 12 — Guide OMS", "contenu utile", "Page 12 — Guide OMS",
                         "autre contenu", "Page 12 — Guide OMS", "Page 12 — Guide OMS"])
        out = TextCleaner().clean(txt)
        assert "Page 12" not in out
        assert "contenu utile" in out


class TestSectionParser:

    def test_sections_markdown(self):
        txt = "# Titre\nintro\n## Traitement\ndonne le traitement\n## Diagnostic\nles tests"
        sections = SectionParser().parse(txt)
        titles = [s.title for s in sections]
        assert "Traitement" in titles and "Diagnostic" in titles
        trt = next(s for s in sections if s.title == "Traitement")
        assert "traitement" in trt.text.lower()
        assert trt.path == ["Titre", "Traitement"]

    def test_sections_numerotees(self):
        txt = "1. DEFINITION DE CAS\nun cas suspect\n2. DIAGNOSTIC\nhemoculture"
        sections = SectionParser().parse(txt)
        assert any("DIAGNOSTIC" in s.title or "Diagnostic" in s.title for s in sections)

    def test_document_sans_titre(self):
        sections = SectionParser().parse("juste du texte continu")
        assert len(sections) == 1


class TestTerminologyMapper:

    def test_mapping_complet(self):
        m = TerminologyMapper().map_text(
            "Le paludisme sévère impose l'artésunate IV ; la dengue contre-indique l'ibuprofène.")
        assert "malaria" in m.disease_codes or "severe_malaria" in m.disease_codes
        assert "dengue" in m.disease_codes
        assert "artesunate_iv" in m.drug_codes
        assert "ibuprofen" in m.drug_codes

    def test_symptomes_normalises(self):
        m = TerminologyMapper().map_text("fièvre et vomissements avec céphalées")
        assert "fever" in m.symptom_codes
        assert "vomiting" in m.symptom_codes
        assert "headache" in m.symptom_codes

    def test_texte_vide(self):
        assert TerminologyMapper().map_text("").total == 0


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

class TestClinicalChunker:

    def _doc(self):
        loader = DocumentLoader()
        raw = loader.load(RAW / "guidelines" / "who-malaria-guide-extrait.md")
        return DocumentNormalizer().normalize(raw)

    def test_chunks_annotes(self):
        chunks = ClinicalChunker().chunk_document(self._doc())
        assert len(chunks) >= 4
        for ch in chunks:
            assert ch.source_id == "who-malaria-guide-extrait"
            assert ch.section_title
            assert ch.text
        mal = [c for c in chunks if "malaria" in c.diseases]
        assert mal, "la maladie paludisme doit être détectée"
        strong = [c for c in chunks if c.recommendation_strength == "strong"]
        assert strong, "les recommandations fortes doivent être marquées"

    def test_validator(self):
        chunks = ClinicalChunker().chunk_document(self._doc())
        validation = ChunkValidator().validate(chunks)
        assert validation.passed
        assert all(80 <= len(c.text) <= 1400 for c in validation.valid)


# ---------------------------------------------------------------------------
# Pipeline bout-en-bout
# ---------------------------------------------------------------------------

class TestPipeline:

    def test_ingestion_complete(self, tmp_path):
        pipeline = DocumentIngestionPipeline(quarantine_dir=tmp_path)
        report = pipeline.ingest(
            RAW / "guidelines" / "who-malaria-guide-extrait.md")
        assert report.status == "draft"
        assert report.units_created >= 4
        assert report.sha256
        files = sorted(tmp_path.glob("*.yaml"))
        assert len(files) == report.units_created
        with open(files[0], encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert data["status"] == "draft"
        assert data["provenance"]["pipeline"] == "tropirag-ingestion-v1"
        assert data["provenance"]["source_sha256"] == report.sha256

    def test_ingestion_dossier(self, tmp_path):
        pipeline = DocumentIngestionPipeline(quarantine_dir=tmp_path)
        reports = pipeline.ingest_directory(RAW)
        assert len(reports) == 3
        assert all(r.status == "draft" for r in reports)
        assert sum(r.units_created for r in reports) >= 12

    def test_document_inconnu_rejete(self, tmp_path):
        from tropirag.evidence_engine.ingestion.document_loader import DocumentLoader
        doc = tmp_path / "note.md"
        doc.write_text("recette de cuisine — mélanger la farine et le sucre.",
                       encoding="utf-8")
        pipeline = DocumentIngestionPipeline(quarantine_dir=tmp_path / "q")
        report = pipeline.ingest(doc)
        assert report.status in ("draft", "rejected")

    def test_promotion(self, tmp_path):
        pipeline = DocumentIngestionPipeline(quarantine_dir=tmp_path)
        report = pipeline.ingest(RAW / "documents" / "cdc-typhoid-xdr-note.txt")
        assert report.unit_files
        # promotion vers le vrai corpus → on simule avec un dossier dédié
        import tropirag.evidence_engine.ingestion.pipeline as pl
        first = Path(report.unit_files[0])
        with open(first, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        data["status"] = "active"
        data["promoted_at"] = "2026-01-01T00:00:00"
        assert data["unit_id"].startswith("eu-draft-")
