"""Descripteur de gouvernance — investigation MEDISUITE-CI-01, verrou M+18.

Source de vérité unique de l'état réglementaire du module CDS :

    « Sorties IA NON VALIDÉES cliniquement — investigation R6-R8 en cours,
      verrou M+18 ; toute décision clinique sur ces sorties est interdite. »

La phrase est identique au bandeau portail (clé i18n scr.ai_banner) — un
seul libellé réglementaire, affiché et appliqué. Le descripteur est porté
par des constantes immuables ; le mode `certified` (après marquage CE)
exige un opt-in explicite à double clé d'environnement, sinon le verrou
reste posé (fail-closed : toute valeur inconnue → locked).

Calendrier M+ : M0 est le jalon de déploiement de l'investigation ; les
fenêtres R5→R8 (plan de validation v1.0.0) sont exprimées en mois pleins
depuis M0. Le verrou de base M+18 clôt R6 (inclusions + monitoring) ; il
est suivi de R7 (rapport clinique MEDDEV 2.7/1) puis R8 (notifié, CE).
"""
from __future__ import annotations

import os
from datetime import date
from typing import Any

__all__ = [
    "GOVERNANCE_DESCRIPTOR",
    "PROTOCOL",
    "PHASES_IN_PROGRESS",
    "LOCK_LABEL",
    "BANNER_TEXT",
    "FORBIDDEN_ACTION",
    "DECISION_PATHS",
    "governance_mode",
    "is_decisional_use_allowed",
    "stamp",
    "add_months",
    "m18_date",
    "m18_status",
    "finalize_denial",
]

# --- descripteur réglementaire (immuable) ----------------------------------

PROTOCOL = "MEDISUITE-CI-01"

PHASES_IN_PROGRESS: tuple[str, ...] = ("R6", "R7", "R8")

LOCK_LABEL = "M+18"

#: Libellé unique — identique à la clé i18n portail `scr.ai_banner` (4 langues).
BANNER_TEXT = (
    "Sorties IA NON VALIDÉES cliniquement — investigation R6-R8 en cours, "
    "verrou M+18 ; toute décision clinique sur ces sorties est interdite."
)

FORBIDDEN_ACTION = "toute décision clinique sur ces sorties est interdite"

_REFS = (
    "MDR (UE) 2017/745 Annexe XV — investigation clinique",
    "ISO 14155 — bonnes pratiques cliniques",
    "MEDDEV 2.7/1 rev 4 — évaluation clinique (R7, ADR-0026)",
    "Protocole TD-10 v1.0 — compliance/mdr/technical-documentation/"
    "10-protocole-investigation-multicentrique-R5.md",
)

#: Chemins API dont la réponse matérialise une sortie d'investigation
#: (tampon `governance` injecté dans le corps + en-têtes).
DECISION_PATHS: tuple[str, ...] = (
    "/api/v1/cases",
    "/api/v1/clinical",
    "/api/v1/evidence",
    "/api/v1/surveillance",
)


def governance_mode() -> str:
    """Mode effectif — fail-closed : `certified` exige le double opt-in
    (MEDISUITE_GOVERNANCE_MODE=certified ET MEDISUITE_GOVERNANCE_CE_ACK=ce),
    toute autre valeur (y compris inconnue) retombe sur `locked`."""
    mode = (os.getenv("MEDISUITE_GOVERNANCE_MODE") or "").strip().lower()
    if mode == "certified" and (os.getenv("MEDISUITE_GOVERNANCE_CE_ACK") or "").strip() == "ce":
        return "certified"
    return "locked"


def is_decisional_use_allowed() -> bool:
    """True uniquement après marquage CE effectif (double opt-in)."""
    return governance_mode() == "certified"


def stamp() -> dict[str, Any]:
    """Bloc `governance` injecté dans les sorties décisionnelles."""
    allowed = is_decisional_use_allowed()
    return {
        "statut": "certified" if allowed else "investigation",
        "protocole": PROTOCOL,
        "phases_en_cours": [] if allowed else list(PHASES_IN_PROGRESS),
        "verrou": LOCK_LABEL,
        "decision_clinique": "autorisée" if allowed else "interdite",
        "avis": BANNER_TEXT,
        "references": _REFS,
    }


GOVERNANCE_DESCRIPTOR = stamp()


# --- calendrier M+ (mois pleins depuis M0) ----------------------------------


def add_months(d: date, months: int) -> date:
    """Décalage calendaire en mois pleins (clamp fin de mois : 31/02 → 28/02)."""
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date(y, m, day)


def m18_date(m0: date) -> date:
    """Date du verrou de base M+18 (clôture R6 — inclusions + monitoring)."""
    return add_months(m0, 18)


def m18_status(today: date, m0: date) -> dict[str, Any]:
    """État du verrou M+18 pour `today` — phase dérivée SANS horloge mondiale
    (réplique la logique portail features/study/status-logic.ts activePhase) :
    verrou non posé → R6 (inclusions/monitoring) ; posé → R7 (rapport clinique) ;
    l'entrée en R8 est une décision humaine (notifié) — non dérivable.
    Le mode `certified` (double opt-in) est l'unique sortie du régime."""
    m18 = m18_date(m0)
    locked = today >= m18
    allowed = is_decisional_use_allowed()
    phase = "R7" if locked else "R6"
    months_elapsed = (today.year - m0.year) * 12 + (today.month - m0.month)
    if today.day < m0.day and months_elapsed > 0:
        months_elapsed -= 1
    return {
        "m0": m0.isoformat(),
        "verrou_m18": m18.isoformat(),
        "pose": locked,
        "phase_active": phase,
        "phases_en_cours": list(PHASES_IN_PROGRESS) if not allowed else [],
        "mois_ecoules": months_elapsed,
        "jours_avant_verrou": max(0, (m18 - today).days),
        "decision_clinique": "autorisée" if allowed else "interdite",
    }


# --- garde fail-closed (451) ------------------------------------------------


def finalize_denial(case_id: str | None = None) -> dict[str, Any]:
    """Corps structuré du refus 451 — matérialisation de l'interdiction.
    `451 Unavailable For Legal Reasons` : la non-disponibilité est LEGALE
    (régime d'investigation), pas technique."""
    body = {
        "error": "clinical_decision_locked",
        "status_code": 451,
        "governance": stamp(),
        "explication": (
            "La matérialisation d'une décision clinique à partir d'une sortie "
            "TropiRAG est interdite tant que l'investigation MEDISUITE-CI-01 "
            "n'est pas close (rapport clinique R7 + marquage CE R8). Les "
            "sorties restent consultables à titre d'investigation uniquement."
        ),
        "reprise": "après marquage CE (fenêtre R8, M+21 → M+30+) + double opt-in",
        "journal": "audit:governance.decision.denied",
    }
    if case_id:
        body["case_id"] = case_id
    return body


# --- m0 par défaut (simulation) ---------------------------------------------

#: Jalon de déploiement de l'investigation (M0) — surcharge via
#: MEDISUITE_GOVERNANCE_M0 (ISO 8601). Défaut aligné sur la simulation
#: du plan de validation : 2025-06-01 → verrou M+18 le 2026-12-01.
def default_m0() -> date:
    raw = (os.getenv("MEDISUITE_GOVERNANCE_M0") or "").strip()
    if raw:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            pass
    return date(2025, 6, 1)

