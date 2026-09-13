"""Gestion des modalités manquantes (ADR-0018) — le cœur de la résilience.

Politique :
1. Une modalité absente est MARQUÉE (présence 0), jamais une erreur.
2. La confiance est recalibrée : facteur = masse des portes présentes / total.
3. Des suggestions cliniques sont émises (biologie peu coûteuse, chaîne PACS…).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MissingModalityReport:
    modalites_attendues: list[str]
    modalites_presentes: list[str]
    modalites_absentes: list[str]
    actions: list[str] = field(default_factory=list)

    @property
    def complet(self) -> bool:
        return not self.modalites_absentes

    def to_dict(self) -> dict:
        return {"attendues": self.modalites_attendues,
                "presentes": self.modalites_presentes,
                "absentes": self.modalites_absentes,
                "complet": self.complet, "actions": self.actions}


class MissingModalityHandler:
    """Analyse le jeu de modalités reçu et produit le rapport + recommandations."""

    def __init__(self, expected: list[str]) -> None:
        self.expected = list(expected)

    def analyze(self, provided: list[str]) -> MissingModalityReport:
        present = [m for m in self.expected if m in provided]
        missing = [m for m in self.expected if m not in provided]
        report = MissingModalityReport(
            modalites_attendues=self.expected, modalites_presentes=present,
            modalites_absentes=missing)
        if not present:
            report.actions.append("ERREUR : aucune modalité fournie")
        elif missing:
            report.actions.append(
                f"inférence dégradée : {len(missing)} modalité(s) manquante(s) — "
                "confiance recalibrée")
            if "tabulaire" in missing:
                report.actions.append(
                    "suggestion : la biologie (tabulaire) est peu coûteuse — "
                    "l'ajouter améliorerait nettement la confiance")
            if "imaging_2d" in missing or "imaging_3d" in missing:
                report.actions.append(
                    "suggestion : imagerie absente — vérifier la chaîne PACS "
                    "(runbook rb-010-missing-modality-cascade)")
        else:
            report.actions.append("modalités complètes — confiance nominale")
        return report

    @staticmethod
    def confidence_adjustment(present: list[str], gates: dict[str, float]) -> float:
        """Facteur de recalibrage : masse des portes des modalités présentes."""
        total = sum(gates.values()) or 1.0
        mass_present = sum(gates.get(m, 0.0) for m in present)
        return mass_present / total
