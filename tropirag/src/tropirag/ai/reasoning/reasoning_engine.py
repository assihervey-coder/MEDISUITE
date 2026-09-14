"""Moteur de raisonnement — audit logique déterministe + DeepSeek-R1 encadré.

L'audit VÉRIFIE (cohérence, contradiction, couverture) ; il ne crée rien.
La version déterministe fonctionne sans modèle : c'est elle qui référence
le comportement attendu de l'audit IA.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from tropirag.ai.guards.output_guard import HallucinationGuard
from tropirag.domain.clinical_case.entities import ClinicalCase
from tropirag.domain.evidence.entities import EvidencePack


@dataclass(slots=True)
class ReasoningAudit:
    """Résultat de l'audit logique d'une synthèse candidate."""

    consistent: bool = True
    contradictions: list[str] = field(default_factory=list)
    uncovered_findings: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    coverage: float = 1.0
    auditor: str = "deterministic"          # deterministic | deepseek-r1

    @property
    def ok(self) -> bool:
        return self.consistent and self.coverage >= 0.8 and not self.contradictions

    def to_dict(self) -> dict:
        return {"consistent": self.consistent, "contradictions": self.contradictions,
                "uncovered_findings": self.uncovered_findings,
                "unsupported_claims": self.unsupported_claims,
                "coverage": round(self.coverage, 3), "auditor": self.auditor}


class ReasoningEngine:
    """Audit déterministe : couverture des résultats de règles + ancrage preuve.

    L'audit IA (DeepSeek-R1) ÉTEND cet audit ; il ne le remplace jamais.
    Une règle de sécurité ne peut JAMAIS être annulée par l'auditeur.
    """

    def __init__(self) -> None:
        self._hg = HallucinationGuard()

    def audit(self, synthesis_text: str, required_messages: list[str],
              pack: EvidencePack, case: ClinicalCase | None = None) -> ReasoningAudit:
        a = ReasoningAudit()

        # 1) couverture : les messages critiques des règles doivent apparaître
        if required_messages:
            low = synthesis_text.lower()
            missing = []
            for msg in required_messages:
                # au moins un mot-clé significatif du message doit être présent
                keywords = [w for w in re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ]{5,}", msg.lower())]
                if keywords and not any(k in low for k in keywords):
                    missing.append(msg)
            a.uncovered_findings = missing
            total = len(required_messages)
            covered = total - len(missing)
            a.coverage = covered / total if total else 1.0

        # 2) contractions internes : mentions de médicaments interdits
        forbidden = ("ibuprofène", "ibuprofen", "aspirine", "aspirin", "diclofénac")
        mentions = [m for m in forbidden if m in synthesis_text.lower()]
        if mentions and any("dengue" in (pack.query + synthesis_text).lower() for _ in [1]):
            # un AINS cité n'est pas automatiquement une contradiction :
            # seulement si recommandé positivement
            for m in mentions:
                if re.search(rf"(?:administrer|donner|prescrire|utiliser)\s+[^.]{{0,40}}{m}",
                             synthesis_text.lower()):
                    a.contradictions.append(
                        f"Recommandation d'un AINS ({m}) dans un contexte où il est contre-indiqué")

        # 3) affirmations non ancrées (réutilise le HallucinationGuard en mode info)
        hg = self._hg.check(synthesis_text, pack)
        if not hg.passed:
            a.unsupported_claims.append(hg.message)

        a.consistent = not a.contradictions
        return a
