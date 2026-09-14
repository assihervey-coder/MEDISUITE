"""Drug Agent — extraction IA + vérification DÉTERMINISTE des contraintes."""
from __future__ import annotations

from typing import Any

from tropirag.ai.agents.base_agent import AgentReport, BaseAgent
from tropirag.domain.medications.constraints import check_drug_for_context
from tropirag.domain.medications.entities import normalize_drug_name
from tropirag.domain.medications.interactions import check_interaction
from tropirag.domain.medications.prescriptions import MedicationOrder


class DrugAgent(BaseAgent):
    """PRINCIPE ABSOLU : LLM extrait (noms) ; le moteur déterministe tranche.

    Aucune dose ne sort jamais d'un LLM. Les vérifications (contre-indications,
    interactions, contexte patient) sont 100 % déterministes.
    """

    name = "drug_agent"
    mission = "Sécurité médicamenteuse : extraction + vérification déterministe."

    def _execute(self, report: AgentReport, medications: list[MedicationOrder] | None = None,
                 suspected: list[str] | None = None, patient_flags: list[str] | None = None,
                 **kwargs: Any) -> None:
        suspected = suspected or []
        patient_flags = patient_flags or []
        checks: list[dict] = []
        codes: list[str] = []
        for m in medications or []:
            code = m.drug_code or normalize_drug_name(m.raw_name)
            if not code:
                checks.append({"raw": m.raw_name, "status": "unknown",
                               "message": "hors référentiel — vérification manuelle requise"})
                continue
            codes.append(code)
            res = check_drug_for_context(code, suspected, patient_flags)
            checks.append({"drug": code, "raw": m.raw_name,
                           "allowed": res.allowed, "severity": res.severity,
                           "reason": res.reason})
        # interactions deux à deux
        interactions: list[dict] = []
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                inter = check_interaction(codes[i], codes[j])
                if inter:
                    interactions.append({"pair": [codes[i], codes[j]], "warning": inter})
        report.output = {"checks": checks, "interactions": interactions}
        report.status = "ok"
        if any(not c.get("allowed", True) for c in checks):
            report.notes.append("contre-indication(s) active(s) détectée(s)")
