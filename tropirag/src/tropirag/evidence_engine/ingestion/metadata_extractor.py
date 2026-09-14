"""Extracteur de métadonnées — inférence déterministe depuis le contenu.

Devine (sans réseau, sans appel IA) :
    - l'autorité source (OMS/MSF/CDC/MSP/national…) via signatures,
    - la juridiction (CI, SN, GH, INT…),
    - la date d'édition (ISO la plus récente citée dans le document),
    - la langue (fr/en par drapeaux lexicaux),
    - le type de document (guideline/protocole/note épidémio…).

L'extraction est CONSERVATRICE : en cas de doute → 'unknown' et c'est
l'humain qui tranche au moment de la validation en quarantaine.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field


@dataclass(slots=True)
class ExtractedMetadata:
    """Métadonnées inférées — à confirmer par un validateur humain."""

    title: str = ""
    authority: str = "unknown"          # WHO | MSF | CDC | NATIONAL | INSTITUTIONAL | SCIENTIFIC | UNKNOWN
    jurisdiction: str = "INT"
    edition_date: str | None = None     # ISO YYYY-MM-DD
    document_type: str = "guideline"
    language: str = "fr"
    confidence: float = 0.0
    evidence_hints: list[str] = field(default_factory=list)

    def as_source_dict(self) -> dict:
        return {
            "authority": self.authority,
            "jurisdiction": self.jurisdiction,
            "title": self.title,
            "edition_date": self.edition_date,
            "document_type": self.document_type,
        }


# signatures d'autorité : (regex, autorité, poids)
_AUTHORITY_SIGNATURES: list[tuple[str, str, float]] = [
    (r"\b(?:organisation mondiale de la sant[ée]|world health organization|"
     r"\boms\b|\bwho\b|geneva|gen[èe]ve)\b", "WHO", 0.6),
    (r"\bm[ée]decins sans fronti[èe]res\b|\bmsf\b|ocp|paris", "MSF", 0.6),
    (r"\bcenters for disease control\b|\bcdc\b|atlanta", "CDC", 0.6),
    (r"\bminist[èe]re de la sant[ée]\b|\bmsp\b|c[ôo]te d[']?ivoire|abidjan", "NATIONAL", 0.55),
    (r"\bannales\b|\bjournal\b|\bstudy\b|\betude\b|\b[ée]tude\b|doi\.org|pubmed", "SCIENTIFIC", 0.4),
    (r"\bunicef\b|\bnicd\b|\bpasteur\b|\binstitut\b", "INSTITUTIONAL", 0.4),
]

_DOC_TYPE_SIGNATURES: list[tuple[str, str]] = [
    (r"protocole|proc[ée]dure op[ée]rationnelle|standard operating", "protocol"),
    (r"note de synth[èe]se|rapport [ée]pid[ée]miologique|bulletin|surveillance", "epidemiology"),
    (r"guide|directive|recommandation|guideline|guidance", "guideline"),
    (r"fiche pratique|checklist|algorithme", "checklist"),
]

_DATE_PATTERNS = [
    r"\b(\d{4})-(\d{2})-(\d{2})\b",                       # 2024-03-15
    r"\b(\d{1,2})[ /](janvier|f[ée]vrier|mars|avril|mai|juin|juillet|"
    r"ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)[ /](\d{4})\b",
    r"\b(january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\s+(\d{1,2}),?\s+(\d{4})\b",
    r"\b(\d{4})\b",                                        # année seule (dernier recours)
]

_FR_FLAGS = r"\ble\b|\bles\b|\bdes\b|\bune?\b|\bet\b|\bdans\b|\bpour\b"
_EN_FLAGS = r"\bthe\b|\band\b|\bof\b|\bwith\b|\bshould\b|\bmust\b"


class MetadataExtractor:
    """Inférence déterministe des métadonnées d'un document."""

    def extract(self, content: str, source_id: str = "",
                head: str = "") -> ExtractedMetadata:
        text = head or content
        low = (head or content).lower()[:4000]  # les métadonnées vivent en tête
        meta = ExtractedMetadata()

        # --- titre : première ligne non vide, privée des marqueurs md -------
        for line in text.splitlines():
            t = line.strip().lstrip("#").strip()
            if len(t) >= 8 and not t.startswith(("[", "!", "---")):
                meta.title = t[:160]
                break
        if not meta.title and source_id:
            meta.title = source_id.replace("-", " ").replace("_", " ").strip().title()

        # --- autorité (vote pondéré) ------------------------------------------
        scores: dict[str, float] = {}
        for pat, authority, weight in _AUTHORITY_SIGNATURES:
            n = len(re.findall(pat, low))
            if n:
                scores[authority] = scores.get(authority, 0.0) + weight * min(n, 4)
        if scores:
            best = max(scores, key=scores.get)  # type: ignore[arg-type]
            meta.authority = best
            meta.confidence = min(0.95, scores[best] / 2.0)

        # --- juridiction --------------------------------------------------
        if re.search(r"c[ôo]te d[']?ivoire|abidjan|bouak[ée]|san-p[ée]dro|korhogo", low):
            meta.jurisdiction = "CI"
        elif re.search(r"\bs[ée]n[ée]gal|dakar\b", low):
            meta.jurisdiction = "SN"
        elif re.search(r"\bghana|accra\b", low):
            meta.jurisdiction = "GH"
        elif meta.authority in ("WHO", "MSF", "CDC"):
            meta.jurisdiction = "INT"

        # --- date d'édition : la plus récente citée -------------------------
        meta.edition_date = self._latest_date(low)

        # --- type de document -------------------------------------------------
        for pat, dtype in _DOC_TYPE_SIGNATURES:
            if re.search(pat, low):
                meta.document_type = dtype
                break

        # --- langue --------------------------------------------------------
        fr = len(re.findall(_FR_FLAGS, low))
        en = len(re.findall(_EN_FLAGS, low))
        meta.language = "fr" if fr >= en else "en"

        return meta

    # ------------------------------------------------------------------
    def _latest_date(self, low: str) -> str | None:
        best: tuple[int, int, int] | None = None
        for m in re.finditer(_DATE_PATTERNS[0], low):
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1990 <= y <= int(time.strftime("%Y")) + 1 and 1 <= mo <= 12 and 1 <= d <= 31:
                cur = (y, mo, d)
                if best is None or cur > best:
                    best = cur
        if best:
            return f"{best[0]:04d}-{best[1]:02d}-{best[2]:02d}"
        # mois français
        mois = {"janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
                "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
                "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12}
        for m in re.finditer(_DATE_PATTERNS[1], low):
            d, name, y = int(m.group(1)), m.group(2), int(m.group(3))
            if name in mois and 1990 <= y <= int(time.strftime("%Y")) + 1:
                cur = (y, mois[name], d)
                if best is None or cur > best:
                    best = cur
        if best:
            return f"{best[0]:04d}-{best[1]:02d}-{best[2]:02d}"
        # année seule
        years = [int(y) for y in re.findall(r"\b(19[89]\d|20[0-4]\d)\b", low)]
        years = [y for y in years if 1990 <= y <= int(time.strftime("%Y")) + 1]
        if years:
            return f"{max(years)}-01-01"
        return None
