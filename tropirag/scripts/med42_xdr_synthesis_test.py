#!/usr/bin/env python3
"""Test de la synthèse Med42 sur les cas XDR — branchement réel Ollama.

Ce script vérifie, sur le mesh TROPIRAG **réellement branché en mode
ollama**, que la chaîne complète fonctionne sur les cas de typhoïde XDR :

    payload → règles → preuves → MedicalAgent (Med42 via Ollama)
            → audit déterministe → Safety Gate → réponse citée

Scénarios :
  S1  Suspicion typhoïde, forme modérée, question clinicien « XDR ? »
      → la synthèse IA est AUTORISÉE : elle doit être « ai-validated »,
        citer les preuves XDR [eu-cdc-typ-xdr-…], être auditable et
        dépourvue de toute affirmation autonome ou posologie.
      (NB : un cas XDR *confirmé* ou *retour de zone foyer* est sévère
       par construction → voir S2/S3 — l'architecture suspend alors
       l'IA. C'est l'invariant « IA ≠ autorité clinique ».)
  S2  XDR par retour de zone foyer (sévérité sévère)
      → la synthèse IA est SUSPENDUE par le routeur de risque.
  S3  XDR confirmée au labo, forme sévère (urgence)
      → synthèse suspendue + méropénème + escalade réanimation.
  S4  Dégradation gracieuse : nœud Ollama injoignable
      → le pipeline continue en déterministe intégral, aucune panne.

Modes d'exécution :
  # 1) VRAIS nœuds GPU (TROPIRAG_OLLAMA_NODES requis) :
  TROPIRAG_INFERENCE_MODE=ollama \
  TROPIRAG_OLLAMA_NODES=text=http://node2:11434,reranking=http://node1:11434 \
  python scripts/med42_xdr_synthesis_test.py

  # 2) RÉPÉTITION GÉNÉRALE sans GPU (serveur mock embarqué) :
  python scripts/med42_xdr_synthesis_test.py --mock

  # 3) Vérifier seulement la santé des nœuds :
  python scripts/med42_xdr_synthesis_test.py --health-only
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
SCRIPTS_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Cas cliniques de référence (typhoïde XDR — V1.2/V1.3)
# ---------------------------------------------------------------------------
def make_cases():
    import datetime as dt

    def days_ago(n: int) -> str:
        return (dt.date.today() - dt.timedelta(days=n)).isoformat()

    cases = {
        # S1 — suspicion typhoïde modérée + question clinicien sur le XDR
        #      → la synthèse Med42 est AUTORISÉE (cas non grave) et citera
        #        les preuves XDR du pack (eu-cdc-typ-xdr-…).
        "S1_typhoide_modernee_question_xdr": {
            "payload": {
                "patient": {"age_years": 26},
                "free_text": "fièvre depuis 4 jours, douleurs abdominales, céphalées",
                "travel": {"segments": [{"country": "CI",
                                          "departure": days_ago(30)}]},
            },
            "user_question": "faut-il craindre une souche XDR résistante ?",
        },
        # S2 — XDR par retour de zone foyer (Pakistan) : sévère → IA suspendue
        "S2_xdr_zone_foyer_severe": {
            "payload": {
                "patient": {"age_years": 28},
                "free_text": "fièvre depuis 8 jours, céphalées, douleurs abdominales, constipation",
                "travel": {"segments": [{"country": "PK",
                                          "departure": days_ago(35)}]},
                "vitals": {"temperature_c": 39.1},
            },
            "user_question": "",
        },
        # S3 — XDR confirmée au labo, forme sévère : urgence → IA suspendue
        "S3_xdr_confirmee_severe": {
            "payload": {
                "patient": {"age_years": 41},
                "free_text": "fièvre depuis 12 jours, confusion, douleurs abdominales, vomissements",
                "travel": {"segments": [{"country": "PK",
                                          "departure": days_ago(40)}]},
                "vitals": {"temperature_c": 39.6, "systolic_bp": 88},
                "lab_results": [{"test": "antibiogram", "value": "xdr"},
                                {"test": "wbc", "value": 14200}],
            },
            "user_question": "",
        },
    }
    return cases


# ---------------------------------------------------------------------------
# Vérifications
# ---------------------------------------------------------------------------
PASS, FAIL = "PASS", "FAIL"
_results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    _results.append((name, bool(ok), detail))
    print(f"  [{'OK ' if ok else 'KO '}] {name}" + (f" — {detail}" if detail else ""))
    return bool(ok)


def check_health(gateway, strict_nodes: bool = True) -> None:
    print("\n[0] SANTÉ DES NŒUDS OLLAMA")
    h = gateway.health()
    explicit = set(gateway.family_urls.values()) | set(gateway.replica_urls)
    for url, node in sorted(h["nodes"].items()):
        # le nœud par défaut (localhost:11434) n'est PAS comptabilisé en échec
        # quand des nœuds explicites sont configurés via TROPIRAG_OLLAMA_NODES
        is_default = url == gateway.base_url and url not in explicit
        if node["reachable"] or not (is_default and explicit):
            check(f"nœud {url}", node["reachable"] or not strict_nodes,
                  f"v{node['version']} — {node['models']} modèles — {node['latency_ms']} ms"
                  if node["reachable"] else "non joignable (hors routage explicite)")
    missing = gateway.missing_models(["med42-v2-70b"])
    check("med42-v2-70b disponible",
          "med42-v2-70b" not in missing,
          missing.get("med42-v2-70b", "présent sur un nœud candidat"))


def run_case(orchestrator, name: str, case: dict) -> None:
    from tropirag.response_engine.response_validator import validate_response

    payload = case["payload"]
    user_question = case.get("user_question", "")
    print(f"\n[{name}]")
    t0 = time.perf_counter()
    r = orchestrator.process(payload, user_question=user_question)
    dt_ms = (time.perf_counter() - t0) * 1000
    print(f"  latence pipeline : {dt_ms:.0f} ms — urgence={r.urgency} "
          f"sévérité={r.severity} couche={r.ai_layer}")

    trace = {s["step"]: s for s in (r.provenance or {}).get("trace", [])}
    codes = [f["code"] for f in r.red_flags]

    # — invariants communs ----------------------------------------------------
    check("réponse valide (validate_response)", validate_response(r) == [])
    check("disclaimer présent", bool(r.disclaimer))
    check("règles matchées", bool(r.matched_rule_ids),
          f"{len(r.matched_rule_ids)} règles")

    if name.startswith("S1"):
        diseases = {d["disease"] for d in r.differentials}
        check("typhoïde dans le différentiel", "enteric_fever" in diseases,
              str(sorted(diseases)))
        check("couche ai-validated", r.ai_layer == "ai-validated", r.ai_layer)
        check("synthèse IA présente", bool(r.ai_synthesis))
        if r.ai_synthesis:
            cited = re.findall(r"\[([a-z0-9-]+)\]", r.ai_synthesis)
            check("citations [eu-…] dans la synthèse", bool(cited),
                  f"{len(cited)} citation(s) : {cited[:5]}")
            typ_units = [c for c in cited if "xdr" in c or "typ" in c]
            check("preuves typhoïde/XDR effectivement citées", bool(typ_units),
                  str(typ_units[:3]))
            check("pas de diagnostic autonome",
                  not re.search(r"diagnostic (certain|confirmé|définitif)",
                                r.ai_synthesis, re.I))
            check("pas de posologie générée par l'IA",
                  not re.search(r"\b\d+\s?(mg|µg|ml)\b", r.ai_synthesis))
        audit = r.audit_summary or {}
        check("audit déterministe réussi", audit.get("consistent", False)
              and audit.get("coverage", 0) >= 0.8,
              f"couverture={audit.get('coverage')}")
        step = trace.get("ai_synthesis", {})
        check("modèle exécutant = Med42",
              str(step.get("model", "")).startswith("med42"),
              str(step.get("model")))
        check("preuves XDR dans le pack",
              any("xdr" in u for u in (r.provenance or {}).get("evidence_units", [])),
              str((r.provenance or {}).get("evidence_units", [])[:5]))
    else:
        # S2/S3 : sévère/urgent → synthèse IA suspendue par conception
        check("drapeau XDR posé",
              any("xdr" in c for c in codes), ", ".join(codes))
        check("synthèse IA suspendue (cas grave — invariant)",
              r.ai_layer == "deterministic", r.ai_layer)
        check("réponse malgré tout complète", bool(r.narrative) and bool(r.red_flags))
        if name.startswith("S3"):
            recos = {d["drug"] for d in r.drug_constraints if not d["forbidden"]}
            forb = {d["drug"] for d in r.drug_constraints if d["forbidden"]}
            check("méropénème IV indiqué (XDR sévère)", "meropenem" in recos)
            check("fluoroquinolones et céphalosporines interdites",
                  "ciprofloxacin" in forb and "ceftriaxone" in forb)
            check("escalade hospitalière/réanimation",
                  any(e["level"] in ("refer_hospital", "refer_icu", "emergency_transfer")
                      for e in r.escalations),
                  str([e["level"] for e in r.escalations]))


def main() -> int:
    ap = argparse.ArgumentParser(description="Test synthèse Med42 — cas XDR (mode ollama)")
    ap.add_argument("--mock", action="store_true",
                    help="démarre un serveur Ollama simulé en local (aucun GPU requis)")
    ap.add_argument("--health-only", action="store_true",
                    help="vérifie uniquement la santé des nœuds")
    args = ap.parse_args()

    nodes = os.environ.get("TROPIRAG_OLLAMA_NODES", "")
    if args.mock:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from mock_ollama_server import MockOllamaServer

        srv = MockOllamaServer()
        url = srv.start_background()
        os.environ["TROPIRAG_OLLAMA_NODES"] = f"text={url}"
        nodes = os.environ["TROPIRAG_OLLAMA_NODES"]
        print(f"[mock] serveur Ollama simulé démarré sur {url}")
    elif not nodes:
        print("ERREUR : définir TROPIRAG_OLLAMA_NODES "
              "(ex. text=http://node2:11434) ou utiliser --mock")
        return 2

    os.environ.setdefault("TROPIRAG_INFERENCE_MODE", "ollama")
    print(f"[config] TROPIRAG_INFERENCE_MODE={os.environ['TROPIRAG_INFERENCE_MODE']}")
    print(f"[config] TROPIRAG_OLLAMA_NODES={nodes}")

    from tropirag.ai.gateways.ollama_gateway import OllamaGateway
    from tropirag.response_engine.response_orchestrator import ResponseOrchestrator

    gw = OllamaGateway.from_env()
    check_health(gw)
    if args.health_only:
        return summarize()

    orchestrator = ResponseOrchestrator(inference_mode="ollama")
    cases = make_cases()

    for name, case in cases.items():
        run_case(orchestrator, name, case)

    # S4 — dégradation gracieuse : nœud injoignable
    print("\n[S4_dégradation_nœud_injoignable]")
    from tropirag.response_engine.response_orchestrator import process_case
    saved = os.environ["TROPIRAG_OLLAMA_NODES"]
    os.environ["TROPIRAG_OLLAMA_NODES"] = "text=http://127.0.0.1:1"
    try:
        r = process_case(cases["S1_typhoide_modernee_question_xdr"]["payload"])
        check("pipeline résiste à l'absence du nœud IA",
              bool(r.narrative) and r.ai_layer == "deterministic",
              f"couche={r.ai_layer}")
        check("règles et preuves toujours servies",
              bool(r.matched_rule_ids) and bool(r.citations))
    finally:
        os.environ["TROPIRAG_OLLAMA_NODES"] = saved

    return summarize()


def summarize() -> int:
    print("\n" + "=" * 78)
    passed = sum(1 for _, ok, _ in _results if ok)
    failed = [n for n, ok, _ in _results if not ok]
    print(f"RÉSULTAT : {passed}/{len(_results)} contrôles OK")
    if failed:
        print("ÉCHECS :")
        for n in failed:
            print(f"  !! {n}")
        return 1
    print("Chaîne Med42/Ollama validée de bout en bout sur les cas XDR.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
