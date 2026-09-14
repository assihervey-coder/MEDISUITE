"""Chunker clinique — sections → passages citables, contexte préservé.

Différences avec le chunker sémantique générique :
    - chaque chunk porte sa section (titre + chemin) et ses maladies,
    - les recommandations fortes (« doit », « recommandé », « ne jamais »)
      sont marquées — elles seront prioritaires au reranking,
    - aucune recommandation n'est coupée en deux blocs (fusion par phrase),
    - l'annotation terminologique est propagée chunk par chunk.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from tropirag.evidence_engine.chunking.semantic_chunker import SemanticChunker
from tropirag.evidence_engine.normalization.document_normalizer import (
    AnnotatedSection,
    NormalizedDocument,
)
from tropirag.evidence_engine.normalization.terminology_mapper import TerminologyMapper

# détection de force de recommandation
_STRONG_RECS = [
    r"\b(?:doit|doivent|il convient de|recommand[ée]e?s?|indiqu[ée]e?s?|"
    r"administr(?:er|ation) (?:imm[ée]diat|en urgence)|en premi[èe]re (?:intention|ligne))\b",
    r"\b(?:ne jamais|contre-indiqu[ée]e?s?|interdit|proscrire|ne pas administrer)\b",
    r"\bu?rgence\b|\bimm[ée]diatement\b",
]
_WEAK_RECS = r"\b(?:peut(?:être| \w+)?|possible|optionnel|selon contexte|[ée]ventuellement)\b"


@dataclass(slots=True)
class ClinicalChunk:
    """Passage clinique autonome, prêt à devenir une unité de preuve."""

    text: str
    section_title: str
    section_path: list[str]
    diseases: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    symptom_codes: list[str] = field(default_factory=list)
    drug_codes: list[str] = field(default_factory=list)
    test_codes: list[str] = field(default_factory=list)
    recommendation_strength: str = "none"   # strong | weak | none
    source_id: str = ""
    chunk_index: int = 0
    sha_root: str = ""

    def to_evidence_unit_dict(self, unit_id: str) -> dict:
        """Dictionnaire prêt pour un YAML d'unité de preuve (quarantaine)."""
        return {
            "unit_id": unit_id,
            "source_id": self.source_id,
            "text": self.text,
            "section": self.section_title,
            "topics": self.topics,
            "diseases": self.diseases,
            "symptom_codes": self.symptom_codes,
            "drug_codes": self.drug_codes,
            "test_codes": self.test_codes,
            "recommendation_strength": self.recommendation_strength,
            "chunk_index": self.chunk_index,
        }


class ClinicalChunker:
    """Découpe un document normalisé en chunks cliniques annotés."""

    def __init__(self, target_chars: int = 650, max_chars: int = 1100) -> None:
        self._semantic = SemanticChunker(target_chars=target_chars, max_chars=max_chars)
        self._mapper = TerminologyMapper()

    def chunk_document(self, doc: NormalizedDocument) -> list[ClinicalChunk]:
        chunks: list[ClinicalChunk] = []
        idx = 0
        for annotated in doc.sections:
            for text in self._semantic.chunk(annotated.section.text):
                if len(text.strip()) < 40:
                    continue  # poussières de mise en page
                terms = annotated.terms
                # ré-annotation fine sur le chunk exact (plus précise que la section)
                local = self._mapper.map_text(text)
                strength = self._strength(text)
                chunks.append(ClinicalChunk(
                    text=text.strip(),
                    section_title=annotated.section.title,
                    section_path=list(annotated.section.path),
                    diseases=sorted(set(local.disease_codes) or set(terms.disease_codes)),
                    topics=self._topics(annotated, strength),
                    symptom_codes=sorted(set(local.symptom_codes) or set(terms.symptom_codes)),
                    drug_codes=sorted(set(local.drug_codes) or set(terms.drug_codes)),
                    test_codes=sorted(set(local.test_codes) or set(terms.test_codes)),
                    recommendation_strength=strength,
                    source_id=doc.source_id,
                    chunk_index=idx,
                    sha_root=doc.sha256[:12],
                ))
                idx += 1
        return chunks

    # ------------------------------------------------------------------
    @staticmethod
    def _strength(text: str) -> str:
        low = text.lower()
        for pat in _STRONG_RECS:
            if re.search(pat, low):
                return "strong"
        if re.search(_WEAK_RECS, low):
            return "weak"
        return "none"

    @staticmethod
    def _topics(annotated: AnnotatedSection, strength: str) -> list[str]:
        """Topics dérivés du chemin de section + force de recommandation."""
        topics: set[str] = set()
        for part in annotated.section.path:
            p = part.lower()
            if re.search(r"traitement|prise en charge|pharmacolog", p):
                topics.add("treatment")
            if re.search(r"diagnostic|examens|biolog", p):
                topics.add("diagnostics")
            if re.search(r"gravit|alarme|urgence|critique", p):
                topics.add("severity")
            if re.search(r"surveillance|follow", p):
                topics.add("monitoring")
            if re.search(r"pr[ée]vention|vaccin", p):
                topics.add("prevention")
            if re.search(r"notification|d[ée]claration", p):
                topics.add("notification")
        if strength == "strong":
            topics.add("strong_recommendation")
        return sorted(topics)
