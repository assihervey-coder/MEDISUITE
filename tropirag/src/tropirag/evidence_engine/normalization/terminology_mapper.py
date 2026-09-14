"""Mappeur terminologique — aligne le langage des sources sur le vocabulaire canonique.

Réutilise les registres du domaine (symptômes, maladies, médicaments, tests)
pour annoter un texte avec les codes canoniques TropiRAG. C'est ce qui permet
au BM25 et aux filtres de métadonnées d'opérer sur un vocabulaire unifié même
quand les sources disent « accès pernicieux », « artéméther-luméfantrine » ou
« hémoculture » (variantes terrain).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from tropirag.domain.diseases.entities import DISEASES
from tropirag.domain.diagnostics.entities import TESTS
from tropirag.domain.medications.entities import DRUGS
from tropirag.domain.symptoms.normalization import normalize_symptoms


def _norm(text: str) -> str:
    """Minuscule sans accents — aligné sur la normalisation des symptômes."""
    import unicodedata

    t = unicodedata.normalize("NFKD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t


@dataclass(slots=True)
class TermMapping:
    """Résultat du mapping terminologique d'un passage."""

    symptom_codes: list[str] = field(default_factory=list)
    disease_codes: list[str] = field(default_factory=list)
    drug_codes: list[str] = field(default_factory=list)
    test_codes: list[str] = field(default_factory=list)
    matched_terms: dict[str, str] = field(default_factory=dict)  # terme source → code

    @property
    def total(self) -> int:
        return (len(self.symptom_codes) + len(self.disease_codes)
                + len(self.drug_codes) + len(self.test_codes))


class TerminologyMapper:
    """Annotation terminologique déterministe (dictionnaires du domaine)."""

    def map_text(self, text: str) -> TermMapping:
        result = TermMapping()
        if not text or not text.strip():
            return result
        low = text.lower()
        nrm = _norm(text)

        # --- symptômes : normalisateur canonique du domaine -----------------
        symptoms = normalize_symptoms(text)
        seen: set[str] = set()
        for sym in symptoms:
            code = getattr(sym, "code", None) or getattr(sym, "symptom", "")
            if code and code not in seen:
                seen.add(code)
                result.symptom_codes.append(code)
                result.matched_terms[code] = code

        # --- maladies : code + libellés FR/EN -------------------------------
        disease_terms: list[tuple[str, str]] = []
        for code, dis in DISEASES.items():
            for name in {code.replace("_", " "),
                         getattr(dis, "label_fr", "").lower(),
                         getattr(dis, "label_en", "").lower()}:
                if name and len(name) >= 4:
                    disease_terms.append((_norm(name), code))
        disease_terms.sort(key=lambda p: -len(p[0]))
        d_codes: set[str] = set()
        for term, code in disease_terms:
            if code in d_codes:
                continue
            if re.search(rf"(?<![\wà-ÿ]){re.escape(term)}(?![\wà-ÿ])", nrm):
                d_codes.add(code)
                result.matched_terms[term] = code
        result.disease_codes = sorted(d_codes)

        # --- médicaments ------------------------------------------------------
        drug_terms: list[tuple[str, str]] = []
        for code, med in DRUGS.items():
            for name in {code.replace("_", " "),
                         getattr(med, "label_fr", "").lower()}:
                if name and len(name) >= 4:
                    drug_terms.append((_norm(name), code))
        drug_terms.sort(key=lambda p: -len(p[0]))
        m_codes: set[str] = set()
        for term, code in drug_terms:
            if code in m_codes:
                continue
            if re.search(rf"(?<![\wà-ÿ]){re.escape(term)}(?![\wà-ÿ])", nrm):
                m_codes.add(code)
                result.matched_terms[term] = code
        result.drug_codes = sorted(m_codes)

        # --- tests biologiques -------------------------------------------------
        test_terms: list[tuple[str, str]] = []
        for code, tst in TESTS.items():
            for name in {code.replace("_", " "),
                         getattr(tst, "label_fr", "").lower()}:
                if name and len(name) >= 4:
                    test_terms.append((_norm(name), code))
        test_terms.sort(key=lambda p: -len(p[0]))
        t_codes: set[str] = set()
        for term, code in test_terms:
            if code in t_codes:
                continue
            if re.search(rf"(?<![\wà-ÿ]){re.escape(term)}(?![\wà-ÿ])", nrm):
                t_codes.add(code)
                result.matched_terms[term] = code
        result.test_codes = sorted(t_codes)

        return result
