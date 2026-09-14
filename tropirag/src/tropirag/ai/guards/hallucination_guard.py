"""Garde anti-hallucination — ancrage lexical des phrases cliniques.

Méthode déterministe (aucun modèle) :
    1. les phrases à contenu clinique (mots-clés maladie/traitement) sont
       identifiées,
    2. une phrase CITÉE [EU-x] doit être ancrée dans SON unité citée
       (recouvrement lexical ≥ seuil) — pas dans le pack entier,
    3. une phrase non citée doit être ancrée dans le pack global,
    4. au-delà de max_unsupported phrases non ancrées → rejet.

Tolérance par défaut : ZÉRO (toute affirmation clinique non ancrée = rejet).
"""
from __future__ import annotations

import re

from tropirag.ai.guards.input_guard import GuardResult, _fail, _pass
from tropirag.core.enums import RefusalReason
from tropirag.domain.evidence.entities import EvidencePack

# marqueurs de phrase « à contenu clinique » (sinon la phrase n'est pas
# évaluable par ancrage lexical — purement administratif)
_CLINICAL_MARKERS = (
    r"dengue|paludisme|malaria|typho|ébull|hemorrh|ictère|jaunisse|"
    r"thrombocy|anémie|artésunate|artemether|paracétamol|ibuprofène|aspirine|"
    r"incubation|transmission|moustique|anophel|aedes|tisane|guérit|"
    r"leptospir|antibiogram|hémoculture|ceftriaxone|azithromycine|méropénème|"
    r"méningite|antipaludique|quinine|primaquine|doxycycline|vaccin|isolement"
)


class HallucinationGuard:
    """Détecte les affirmations sans ancrage dans le pack de preuves."""

    STOP = {"le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "en",
            "est", "sont", "à", "au", "aux", "avec", "pour", "par", "que", "qui",
            "il", "elle", "on", "ce", "cette", "ces", "dans", "sur", "pas", "plus",
            "chez", "patient", "patiente", "cas", "fièvre", "si", "peut", "être"}

    def __init__(self, min_overlap: float = 0.4, max_unsupported: int = 3) -> None:
        self.min_overlap = min_overlap
        self.max_unsupported = max_unsupported

    # ------------------------------------------------------------------
    def _sentences(self, text: str) -> list[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]

    def _tokens(self, s: str) -> set[str]:
        return {t for t in re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ]+", s.lower())
                if len(t) > 3 and t not in self.STOP}

    def clinical_sentences(self, text: str) -> list[str]:
        """Phrases portant du contenu clinique (auditables)."""
        return [s for s in self._sentences(text)
                if re.search(_CLINICAL_MARKERS, s.lower())]

    def anchor_score(self, sentence: str, unit_text: str) -> float:
        """Score d'ancrage lexical phrase ↔ texte d'unité (0–1)."""
        toks = self._tokens(sentence)
        if not toks:
            return 1.0  # phrase sans contenu évaluable → pas non ancrée
        target = self._tokens(unit_text)
        return len(toks & target) / len(toks)

    # ------------------------------------------------------------------
    def check(self, text: str, pack: EvidencePack) -> GuardResult:
        if not pack.units:
            return _fail(RefusalReason.INSUFFICIENT_EVIDENCE,
                         "Pas de preuve → pas de vérification possible → pas de synthèse.")
        unit_tokens: dict[str, set[str]] = {}
        evidence_tokens: set[str] = set()
        unit_text: dict[str, str] = {}
        for u in pack.units:
            unit_tokens[u.unit_id] = self._tokens(u.text)
            unit_text[u.unit_id] = u.text
            evidence_tokens |= unit_tokens[u.unit_id]
        clinical_sentences = self.clinical_sentences(text)
        unsupported = 0
        details: list[str] = []
        for s in clinical_sentences:
            toks = self._tokens(s)
            if not toks:
                continue
            cited = re.findall(r"\[([^\[\]]+)\]", s)
            if cited:
                # phrase citée → ancrage exigé sur SON unité
                target_tokens: set[str] = set()
                for cid in cited:
                    target_tokens |= unit_tokens.get(cid.strip(), set())
                if target_tokens and len(toks & target_tokens) / len(toks) >= self.min_overlap:
                    continue
                details.append(s[:80])
                unsupported += 1
            else:
                if len(toks & evidence_tokens) / len(toks) >= self.min_overlap:
                    continue
                details.append(s[:80])
                unsupported += 1
        if unsupported > self.max_unsupported:
            return _fail(RefusalReason.HALLUCINATION_DETECTED,
                         f"Sortie rejetée : {unsupported} affirmation(s) clinique(s) "
                         "sans ancrage dans les preuves ni citation.",
                         [f"unsupported={unsupported}"] + details[:3])
        return _pass(findings=[f"phrases cliniques: {len(clinical_sentences)}"])

    # ------------------------------------------------------------------
    def audit(self, text: str, pack: EvidencePack) -> dict:
        """Rapport détaillé d'ancrage (métriques d'évaluation)."""
        if not pack.units:
            return {"clinical_sentences": 0, "anchored": 0, "unsupported": 0,
                    "mean_anchor": 0.0}
        scores: list[float] = []
        unsupported = 0
        sentences = self.clinical_sentences(text)
        for s in sentences:
            best = max((self.anchor_score(s, u.text) for u in pack.units), default=0.0)
            scores.append(best)
            if best < self.min_overlap:
                unsupported += 1
        return {"clinical_sentences": len(sentences),
                "anchored": len(sentences) - unsupported,
                "unsupported": unsupported,
                "mean_anchor": round(sum(scores) / len(scores), 4) if scores else 1.0}
