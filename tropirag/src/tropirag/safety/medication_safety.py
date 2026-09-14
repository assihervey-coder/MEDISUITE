"""Sécurité médicamenteuse — orchestrateur déterministe des contraintes.

Point d'entrée unique pour toute question « ce médicament est-il sûr dans
ce contexte ? ». Aucune posologie n'est produite ici : on bloque, on
constraind, on documente — la dose relève du protocole et du clinicien.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.ai.agents.drug_agent import DrugAgent  # noqa: F401
from tropirag.domain.medications.constraints import check_drug_for_context  # noqa: F401
from tropirag.domain.medications.entities import DRUGS
from tropirag.domain.medications.interactions import check_interaction  # noqa: F401

# gravité d'un blocage (pour l'ordre d'affichage et la traçabilité)
BLOCK_SEVERITY = {"absolute": 3, "relative": 2, "caution": 1}


@dataclass(slots=True)
class MedicationVerdict:
    drug_code: str
    allowed: bool
    severity: str            # absolute | relative | caution | none
    reasons: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)


class MedicationSafetyEngine:
    """Vérifie un médicament contre TOUT le contexte du cas."""

    def check(self, drug_code: str, context: dict) -> MedicationVerdict:
        """context : {diseases, pregnant, gestational_age_weeks,
        conditions, age, age_months, ...}."""
        verdict = MedicationVerdict(drug_code=drug_code, allowed=True,
                                     severity="none")
        drug = DRUGS.get(drug_code)
        if drug is None:
            verdict.reasons.append("médicament inconnu du registre — prudence maximale")
            verdict.severity = "caution"
            return verdict

        # 1) contre-indications par maladie/état déclaré
        for state, reason in drug.contraindicated_in.items():
            if self._state_present(state, context):
                verdict.allowed = False
                verdict.severity = "absolute"
                verdict.reasons.append(f"contre-indiqué si {state} : {reason}")

        # 2) grossesse
        if context.get("pregnant"):
            cat = drug.pregnancy_category
            if cat in ("D", "X"):
                verdict.allowed = False
                verdict.severity = "absolute"
                verdict.reasons.append(
                    f"catégorie grossesse {cat} — interdit chez la femme enceinte")
            elif cat == "C":
                if verdict.severity == "none":
                    verdict.severity = "relative"
                verdict.reasons.append(
                    "catégorie grossesse C — évaluer le bénéfice/risque")

        # 3) interactions
        for other in context.get("current_medications", []):
            if other in drug.interacts_with:
                if verdict.severity in ("none", "caution"):
                    verdict.severity = "relative"
                verdict.reasons.append(f"interaction documentée avec {other}")

        # 4) âges extrêmes
        age = context.get("age")
        if age is not None and age < 5 and drug.drug_class.lower().find("antipaludique") >= 0:
            if verdict.severity == "none":
                verdict.severity = "caution"
            verdict.reasons.append("enfant < 5 ans — adapter selon protocole pédiatrique")

        verdict.allowed = verdict.severity not in ("absolute",)
        return verdict

    # ------------------------------------------------------------------
    @staticmethod
    def _state_present(state: str, context: dict) -> bool:
        diseases = {str(d).lower() for d in context.get("diseases", [])}
        conditions = {str(c).lower() for c in (context.get("conditions") or [])}
        target = state.lower()
        if target in diseases or target in conditions:
            return True
        # alias grossesse
        if target in ("pregnancy", "grossesse") and context.get("pregnant"):
            return True
        return False


def screen_prescription(drugs: list[str], context: dict) -> list[MedicationVerdict]:
    """Passe tous les médicaments proposés au filtre de sécurité."""
    engine = MedicationSafetyEngine()
    verdicts = [engine.check(d, context) for d in drugs]
    # les blocages absolus en tête — lisibilité clinique
    return sorted(verdicts, key=lambda v: -BLOCK_SEVERITY.get(v.severity, 0))
