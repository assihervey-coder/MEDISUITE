"""Client DeepSeek-R1-Distill — auditeur logique (jamais décideur)."""
from __future__ import annotations

import json

from tropirag.ai.model_client_base import ModelClientBase, load_prompt


class DeepSeekR1Client(ModelClientBase):
    """R1-Distill : vérifie cohérence, contradictions, couverture de preuve.

    Rôle strictement descendant : il AUDITE un projet de synthèse déjà
    produit (déterministe ou Med42). Il ne peut jamais annuler une règle
    de sécurité ni créer du contenu clinique.
    """

    capability = "logical_audit"
    default_model_id = "deepseek-r1-distill-32b"
    temperature = 0.0
    max_tokens = 1024

    def audit_synthesis(self, synthesis_text: str, evidence_text: str,
                        rule_findings: list[str] | None = None,
                        language: str = "fr") -> "object":
        system = load_prompt("SYSTEM_PROMPT", "") or (
            "You are a logic auditor. You verify consistency, detect contradictions, "
            "and check evidence coverage. You produce NO clinical content. Output JSON."
        )
        prompt = (
            "## SYNTHESIS TO AUDIT\n" + synthesis_text + "\n\n"
            "## EVIDENCE\n" + evidence_text + "\n\n"
            "## DETERMINISTIC FINDINGS (must all appear)\n"
            + "\n".join(f"- {f}" for f in (rule_findings or []))
            + "\n\nProduce JSON: {\"consistent\": bool, \"contradictions\": [str], "
              "\"uncovered_findings\": [str], \"unsupported_claims\": [str], "
              "\"coverage\": 0-1}"
        )
        resp = self._run(prompt, system=system, language=language, json_mode=True)
        if resp.ok and resp.structured is None:
            try:
                resp.structured = json.loads(resp.text[resp.text.find("{"):resp.text.rfind("}") + 1])
            except (ValueError, json.JSONDecodeError):
                resp.structured = None
        return resp
