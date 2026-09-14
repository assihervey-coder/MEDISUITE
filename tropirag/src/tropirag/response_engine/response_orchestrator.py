"""Orchestrateur de réponse — le pipeline COMPLET de bout en bout.

    CAS
     → ClinicalOrchestrator (règles + sécurité + temporel + différentiel)
     → QueryPlanner (requête de retrieval)
     → EvidenceAgent → EvidenceEngine → EvidencePack
     → RiskRouter : synthèse IA autorisée ?
         ├─ OUI → MedicalAgent (Med42) → ReasoningEngine (audit) → SafetyGate
         └─ NON → synthèse déterministe
     → ResponseEngine → ClinicalResponse
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.ai.agents.base_agent import BaseAgent
from tropirag.ai.agents.evidence_agent import EvidenceAgent
from tropirag.ai.agents.medical_agent import MedicalAgent
from tropirag.ai.gateways.deterministic_gateway import DeterministicGateway
from tropirag.ai.gateways.inference_gateway import GatewayManager
from tropirag.ai.gateways.ollama_gateway import OllamaGateway
from tropirag.ai.gateways.vllm_gateway import VLLMGateway
from tropirag.ai.registry.model_registry import ModelRegistry, get_registry
from tropirag.ai.reasoning.reasoning_engine import ReasoningEngine
from tropirag.ai.routing.model_router import ModelRouter
from tropirag.ai.routing.risk_router import route_by_risk
from tropirag.clinical_engine.clinical_context import ClinicalContext
from tropirag.clinical_engine.orchestrator import ClinicalAnalysis, ClinicalOrchestrator
from tropirag.core.config import get_config
from tropirag.core.identifiers import new_id
from tropirag.evidence_engine.evidence_engine import EvidenceEngine
from tropirag.query_engine.query_planner import QueryPlanner
from tropirag.response_engine.clinical_response_builder import (
    ClinicalResponse,
    build_narrative,
)
from tropirag.response_engine.citation_builder import attach_citations
from tropirag.response_engine.uncertainty_formatter import attach_uncertainty
from tropirag.safety.clinical_safety import disclaimer as _disclaimer
from tropirag.safety.refusal import build_refusal
from tropirag.safety.safety_gate import SafetyGate


@dataclass(slots=True)
class PipelineTrace:
    """Trace complète du pipeline — auditabilité."""
    steps: list[dict] = field(default_factory=list)

    def add(self, step: str, **kv) -> None:
        self.steps.append({"step": step, **kv})


class ResponseOrchestrator:
    """Le chef d'orchestre final de TropiRAG — détermine la réponse complète."""

    def __init__(self, clinical_orchestrator: ClinicalOrchestrator | None = None,
                 evidence_engine: EvidenceEngine | None = None,
                 inference_mode: str | None = None) -> None:
        self.config = get_config()
        mode = inference_mode or self.config.inference.mode

        self.clinical = clinical_orchestrator or ClinicalOrchestrator()

        # — mesh : gateways selon le mode ————————————————————
        gateways = [DeterministicGateway(dim=self.config.retrieval.vector_dimensions)]
        if mode == "ollama":
            # V1.1 : multi-nœuds via TROPIRAG_OLLAMA_NODES (famille=URL,...)
            gateways.append(OllamaGateway.from_env(self.config.inference.ollama_url,
                                                  self.config.inference.timeout_seconds))
        elif mode == "vllm":
            gateways.append(VLLMGateway(self.config.inference.vllm_url,
                                        self.config.inference.timeout_seconds))
            gateways.append(OllamaGateway.from_env(self.config.inference.ollama_url,
                                                  self.config.inference.timeout_seconds))
        self.gateway_manager = GatewayManager(gateways)
        self.registry: ModelRegistry = get_registry()
        self.router = ModelRouter(self.registry,
                                  self.gateway_manager.health,
                                  inference_mode=mode)
        self.evidence = evidence_engine or EvidenceEngine(self.gateway_manager)

        self.query_planner = QueryPlanner()
        self.reasoning = ReasoningEngine()
        self.safety_gate = SafetyGate()
        self.evidence_agent = EvidenceAgent().bind(self.router, self.gateway_manager, self.registry)
        self.medical_agent = MedicalAgent().bind(self.router, self.gateway_manager, self.registry)

    # ------------------------------------------------------------------
    def process(self, payload: dict, user_question: str = "",
                language: str = "fr", use_ai: bool = True) -> ClinicalResponse:
        trace = PipelineTrace()

        # 1. — analytique déterministe ————————————————
        analysis = self.clinical.analyze_payload(payload)
        trace.add("clinical_analysis", matched=len(analysis.matched_rule_ids),
                  differentials=len(analysis.differentials))

        # 2. — plan de requête + preuves ————————————————
        plan = self.query_planner.plan(analysis, user_question)
        ev_report = self.evidence_agent.run(
            evidence_engine=self.evidence,
            query=plan.retrieval_query,
            diseases=plan.disease_focus,
        )
        pack = ev_report.output.get("pack")
        if pack is None:  # requête vide → pack vide
            from tropirag.domain.evidence.entities import EvidencePack

            pack = EvidencePack(query=plan.retrieval_query)
        trace.add("evidence", units=len(pack.units), status=ev_report.status)

        # 3. — risque : la synthèse IA est-elle autorisée ? ——————————
        risk = route_by_risk(analysis.safety.max_severity, analysis.safety.max_urgency)

        # 4. — synthèse IA encadrée (si autorisée + dispo + preuves) ————
        ai_text: str | None = None
        audit_summary: dict = {}
        refusal: str | None = None
        if use_ai and risk.ai_synthesis_allowed and self.router.is_ai_available() and not pack.empty():
            ctx = ClinicalContext.from_analysis(analysis)
            ev_text = "\n\n".join(
                f"[{u.unit_id}] ({u.source.publisher}, {u.source.title}) {u.text}"
                for u in pack.top(6))
            rep = self.medical_agent.run(
                clinical_context=ctx.case_summary,
                evidence_text=ev_text,
                constraints=ctx.constraints + [risk.reason],
                language=language,
            )
            synth = rep.output.get("synthesis") if rep.output else None
            if synth and synth.get("parse_ok") and synth.get("summary"):
                # audit déterministe du projet de synthèse
                audit = self.reasoning.audit(
                    synth["summary"],
                    required_messages=[rf.message for rf in analysis.rules.red_flags][:5],
                    pack=pack, case=analysis.case)
                audit_summary = audit.to_dict()
                if audit.ok:
                    ai_text = synth["summary"]
                    trace.add("ai_synthesis", model=rep.models_used[0] if rep.models_used else "?")
                else:
                    refusal = build_refusal("hallucination_detected",
                                            f"Audit : couverture {audit.coverage:.0%}.")
                    trace.add("ai_synthesis_rejected", audit=audit_summary)
            else:
                trace.add("ai_synthesis_unavailable", status=rep.status)

        # 5. — Safety Gate : décision finale du mode de sortie ——————————
        gate = self.safety_gate.decide(analysis, pack, ai_text)
        if not gate.allowed and gate.reason is not None:
            refusal = refusal or build_refusal(gate.reason.value)
            ai_text = None
            trace.add("safety_gate", refused=True)
        else:
            trace.add("safety_gate", mode=gate.mode)

        # 6. — construction de la réponse finale ————————————————
        response = self._build_response(analysis, pack, language=language)
        response.ai_layer = "ai-validated" if (gate.mode == "ai" and ai_text) else "deterministic"
        if gate.mode == "ai" and ai_text:
            response.ai_synthesis = ai_text
        response.refusal = refusal
        response.audit_summary = audit_summary
        response.provenance = {
            "trace": trace.steps,
            "matched_rule_ids": analysis.matched_rule_ids,
            "rules_fingerprint": analysis.rules_fingerprint,
            "evidence_units": [u.unit_id for u in pack.units],
        }
        return response

    # ------------------------------------------------------------------
    def _build_response(self, analysis: ClinicalAnalysis, pack, language: str = "fr") -> ClinicalResponse:
        resp = ClinicalResponse(
            case_id=analysis.case.case_id,
            urgency=analysis.safety.max_urgency.value,
            severity=analysis.safety.max_severity.value,
            narrative=build_narrative(analysis, pack),
            differentials=[d.to_dict() for d in analysis.differentials],
            red_flags=[{"code": rf.code, "severity": rf.severity.value,
                        "urgency": rf.urgency.value, "message": rf.message,
                        "rule_id": rf.rule_id} for rf in analysis.rules.red_flags],
            escalations=[{"level": e.level.value, "message": e.message,
                          "rule_id": e.rule_id} for e in analysis.rules.escalations],
            required_tests=[{"test": t.test_code, "reason": t.reason,
                             "rule_id": t.rule_id} for t in analysis.rules.required_tests],
            drug_constraints=[{"drug": dc.drug, "forbidden": dc.forbidden,
                               "reason": dc.reason, "rule_id": dc.rule_id}
                              for dc in analysis.rules.drug_constraints],
            timeline_notes=analysis.timeline_notes,
            notifications=analysis.rules.notifications,
            uncertainty=analysis.uncertainty,
            matched_rule_ids=analysis.matched_rule_ids,
            disclaimer=_disclaimer(language),
        )
        attach_citations(resp, pack)
        attach_uncertainty(resp, analysis)
        return resp


def process_case(payload: dict, **kwargs) -> ClinicalResponse:
    """Point d'entrée fonctionnel simple."""
    return ResponseOrchestrator().process(payload, **kwargs)
