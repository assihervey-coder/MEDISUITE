"""Garde d'entrée — filtrage des requêtes AVANT toute inférence.

Deux familles de menaces :
    1. INJECTION de prompt (détournement du rôle du système),
    2. HORS PÉRIMÈTRE clinique (demandes de diagnostic certain, posologies…).

Règle : ce qui franchit l'entrée n'est jamais une consigne pour le modèle —
les documents/inputs sont traités comme des DONNÉES, jamais des instructions.
"""
from __future__ import annotations

import re

from dataclasses import dataclass, field

from tropirag.core.enums import RefusalReason


# ---------------------------------------------------------------------------
# Contrat commun de toutes les gardes (défini ICI : premier maillon du pipeline)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GuardResult:
    passed: bool
    reason: RefusalReason | None = None
    message: str = ""
    sanitized: str | None = None
    findings: list[str] = field(default_factory=list)


def _pass(msg: str = "", findings: list[str] | None = None) -> GuardResult:
    return GuardResult(passed=True, message=msg, findings=findings or [])


def _fail(reason: RefusalReason, msg: str, findings: list[str] | None = None) -> GuardResult:
    return GuardResult(passed=False, reason=reason, message=msg, findings=findings or [])

# ---------------------------------------------------------------------------
# Signatures d'injection (FR + EN)
# ---------------------------------------------------------------------------
INJECTION_PATTERNS: list[tuple[str, str]] = [
    (r"ignore (?:all )?(?:previous|prior) instructions", "instruction ignorée (EN)"),
    (r"ignore[sz]? (?:toutes )?les? (?:consignes|instructions) (?:pr[ée]c[ée]dentes)", "instruction ignorée (FR)"),
    (r"system prompt", "extraction du prompt système"),
    (r"tu es maintenant", "réassignation de rôle"),
    (r"act as .{0,30}(?:doctor|m[ée]decin)", "usurpation de rôle médical"),
    (r"jailbreak", "jailbreak explicite"),
    (r"developer mode", "mode développeur"),
    (r"r[ée]v[èe]le tes instructions", "extraction des consignes"),
    (r"donne-moi ta consigne", "extraction des consignes"),
    (r"<\|.*?\|>", "jetons de contrôle factices"),
    (r"dis(?:-| )?moi comment fabriquer", "fabrication dangereuse"),
    (r"\bDAN\b|\bdo anything now\b", "DAN jailbreak"),
]

# ---------------------------------------------------------------------------
# Demandes hors périmètre clinique V1
# ---------------------------------------------------------------------------
OUT_OF_SCOPE_PATTERNS: list[tuple[str, str]] = [
    (r"pos[ée]s? un diagnostic", "diagnostic autonome demandé"),
    (r"confirme que", "confirmation diagnostique demandée"),
    (r"c'est certainement", "certitude demandée"),
    (r"quel m[ée]dicament sans ordonnance", "automédication"),
    (r"prescri[st] (?:une )?dose", "prescription hors cadre"),
    (r"combine? ces m[ée]dicaments", "association à aveugle"),
    (r"dose exacte", "posologie par LLM demandée"),
    (r"remplace le m[ée]decin", "substitution du professionnel"),
]


class InputGuard:
    """Filtre les entrées utilisateur avant le mesh IA."""

    def check(self, text: str) -> GuardResult:
        findings: list[str] = []
        low = (text or "").lower()
        for pat, label in INJECTION_PATTERNS:
            if re.search(pat, low):
                findings.append(f"injection: {label}")
        for pat, label in OUT_OF_SCOPE_PATTERNS:
            if re.search(pat, low):
                findings.append(f"out-of-scope: {label}")
        if findings:
            kind = (RefusalReason.INJECTION_DETECTED
                    if any(f.startswith("injection") for f in findings)
                    else RefusalReason.OUTSIDE_SCOPE)
            return _fail(kind,
                         "Requête rejetée par le garde d'entrée "
                         "(injection ou hors périmètre clinique).", findings)
        return _pass()

    # ------------------------------------------------------------------
    def sanitize_document(self, text: str) -> str:
        """Neutralise les tentatives d'injection DANS un document ingéré.

        Un document source peut contenir « ignore previous instructions » :
        ces passages sont neutralisés par balisage afin qu'aucun modèle ne les
        traite comme une consigne. Le texte d'origine reste archivé (audit).
        """
        out = text
        for pat, _ in INJECTION_PATTERNS:
            out = re.sub(pat, "[neutralisé-injection]", out, flags=re.IGNORECASE)
        return out
