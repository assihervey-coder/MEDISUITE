"""RBAC — matrice de rôles et permissions cliniques.

Rôles alignés sur les guides utilisateurs de la spec (docs/user-guides/) :
médecin, radiologue, biologiste, infirmier, pharmacien, anesthésiste,
urgentiste, administrateur, patient.
"""
from __future__ import annotations

PERMISSIONS = [
    "patient.read", "patient.write", "patient.export",
    "imaging.read", "imaging.upload", "imaging.report",
    "lab.order", "lab.validate", "lab.qc",
    "prescription.write", "pharma.dispense",
    "ai.infer", "ai.explain", "ai.train",
    "audit.read", "audit.verify",
    "admin.users", "admin.config",
    "appointment.manage", "billing.manage",
    # Investigation MEDISUITE-CI-01 (eCRF, protocole R5/R6 — v0.7/v0.8)
    "ecrf.read", "ecrf.write", "ecrf.sign", "ecrf.monitor",
    "ecrf.export", "ecrf.adjudicate", "ecrf.lock", "ecrf.extract",
]

ROLES: dict[str, set[str]] = {
    "medecin": {"patient.read", "patient.write", "imaging.read", "imaging.report",
                 "lab.order", "lab.validate", "prescription.write", "ai.infer",
                 "ai.explain", "appointment.manage", "patient.export"},
    "radiologue": {"patient.read", "imaging.read", "imaging.upload", "imaging.report",
                    "ai.infer", "ai.explain", "patient.export"},
    "biologiste": {"patient.read", "lab.order", "lab.validate", "lab.qc", "ai.infer"},
    "infirmier": {"patient.read", "patient.write", "imaging.read",
                   "appointment.manage"},
    "pharmacien": {"patient.read", "prescription.write", "pharma.dispense"},
    "anesthesiste": {"patient.read", "patient.write", "imaging.read", "lab.order"},
    "urgentiste": {"patient.read", "patient.write", "imaging.read", "lab.order",
                    "ai.infer", "appointment.manage"},
    "administrateur": {"admin.users", "admin.config", "audit.read", "audit.verify",
                        "patient.read"},
    "auditeur": {"audit.read", "audit.verify"},
    "patient": set(),  # portail patient : accès géré par consentement explicite
    # --- Investigation MEDISUITE-CI-01 (protocole R5 §8, v0.7) ---------------
    "investigateur": {"ecrf.read", "ecrf.write", "ecrf.sign", "patient.read"},
    "moniteur": {"ecrf.read", "ecrf.monitor"},              # indépendant, contrat
    "adjudicateur": {"ecrf.read", "ecrf.adjudicate"},       # comité aveugle §3.3
    "data_manager": {"ecrf.read", "ecrf.write", "ecrf.export", "ecrf.extract",
                      "audit.read"},
    "promoteur": {"ecrf.read", "ecrf.monitor", "ecrf.export", "ecrf.lock",
                   "audit.read"},
}
# Les cliniciens investigateurs de terrain sont des `medecin` : ils saisissent
# et signent l'eCRF (le rôle dédié `investigateur` est contractuel).
ROLES["medecin"] = ROLES["medecin"] | {"ecrf.read", "ecrf.write", "ecrf.sign"}


def can(role: str, permission: str) -> bool:
    """Vrai si `role` détient `permission`. Rôle inconnu → False (fail-closed)."""
    return permission in ROLES.get(role, set())


def require(role: str, permission: str) -> None:
    """Lève PermissionError si le rôle n'a pas la permission (fail-closed)."""
    if not can(role, permission):
        raise PermissionError(f"rôle '{role}' n'a pas la permission '{permission}'")


def permissions_of(role: str) -> set[str]:
    return frozenset(ROLES.get(role, set()))
