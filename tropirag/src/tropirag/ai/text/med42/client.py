"""Client Med42 — Clinical Reasoner (synthèse clinique encadrée)."""
from __future__ import annotations

import json

from tropirag.ai.model_client_base import ModelClientBase, load_prompt


class Med42Client(ModelClientBase):
    """Med42 v2 (70B) : synthèse clinique SOUS CONTRAT.

    Contrat d'entrée : contexte clinique + pack de preuves + règles matchées.
    Contrat de sortie : JSON structuré, chaque affirmation citée.
    Le Safety Gate peut rejeter la sortie.
    """

    capability = "clinical_reasoning"
    default_model_id = "med42-v2-70b"
    temperature = 0.1
    max_tokens = 2048

    def clinical_synthesis(self, clinical_context: str, evidence_text: str,
                           constraints: list[str] | None = None,
                           language: str = "fr") -> "object":
        system = load_prompt("SYSTEM_PROMPT", "") or (
            "You are a clinical reasoning assistant embedded in a deterministic decision "
            "support system. You MUST ground every statement in the provided evidence. "
            "You NEVER diagnose autonomously. Output JSON only."
        )
        # ⚠️ injection par tokens {{...}} + str.replace — JAMAIS str.format :
        # le contrat de sortie contient des accolades JSON littérales qui
        # feraient échouer .format() (KeyError). (V1.3 — fix branchement réel.)
        tpl = load_prompt("clinical_synthesis", "clinical") or (
            "## CONTEXT\n{{CONTEXT}}\n\n"
            "## EVIDENCE (authoritative, cite as [EU-id])\n{{EVIDENCE}}\n\n"
            "## CONSTRAINTS\n{{CONSTRAINTS}}\n\n"
            "Produce a JSON object with keys: summary (fr), key_findings[], "
            "differential_review[], warnings[], citations[] (list of EU-ids used). "
            "Every clinical statement must map to a citation."
        )
        constraints_block = "\n".join(f"- {c}" for c in (constraints or [])) or "- aucune"
        prompt = (tpl
                  .replace("{{CONTEXT}}", clinical_context)
                  .replace("{{EVIDENCE}}", evidence_text)
                  .replace("{{CONSTRAINTS}}", constraints_block))
        resp = self._run(prompt, system=system, language=language, json_mode=True)
        if resp.ok and resp.structured is None:
            # certains backends ne supportent pas le mode JSON strict
            try:
                resp.structured = json.loads(resp.text[resp.text.find("{"):resp.text.rfind("}") + 1])
            except (ValueError, json.JSONDecodeError):
                resp.structured = None
        return resp
