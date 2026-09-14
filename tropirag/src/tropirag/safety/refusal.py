"""Refus — construction de réponses de refus constructives."""
from __future__ import annotations

from tropirag.core.enums import RefusalReason

REFUSAL_TEMPLATES: dict[str, str] = {
    RefusalReason.INSUFFICIENT_EVIDENCE.value: (
        "Je ne peux pas produire de synthèse clinique car aucune source de référence "
        "(OMS/MSF/CDC) n'a été retrouvée pour cette requête. "
        "Actions possibles : préciser les symptômes et le pays de voyage, "
        "ou appliquer le protocole local. Les alertes de sécurité restent actives."),
    RefusalReason.OUTSIDE_SCOPE.value: (
        "Cette demande sort du périmètre de TropiRAG (fièvre + voyage, appui à la "
        "décision clinique). Consultez un professionnel de santé pour toute autre question."),
    RefusalReason.AUTONOMOUS_DIAGNOSIS_FORBIDDEN.value: (
        "TropiRAG ne pose pas de diagnostic. Je peux fournir un différentiel "
        "pondéré, des tests recommandés et des sources — la décision vous appartient."),
    RefusalReason.SAFETY_OVERRIDE.value: (
        "La sortie générée a été bloquée par la porte de sécurité (posologie ou "
        "formulation interdite). Voici la synthèse déterministe issue des règles."),
    RefusalReason.HALLUCINATION_DETECTED.value: (
        "La sortie générée contenait des affirmations non ancrées dans les sources ; "
        "elle a été rejetée. Voici la synthèse déterministe fondée sur les règles."),
    RefusalReason.INJECTION_DETECTED.value: (
        "Requête rejetée : tentative de manipulation détectée. "
        "Reformulez votre question clinique."),
}


def build_refusal(reason: str, extra: str = "") -> str:
    base = REFUSAL_TEMPLATES.get(reason, "Demande refusée pour raison de sécurité clinique.")
    return base + (f"\n{extra}" if extra else "")
