#!/usr/bin/env python3
"""Simulation du régime d'investigation MEDISUITE-CI-01 — verrou M+18.

Répond en expert médecine/informatique à la question : que se passe-t-il,
mois par mois, pour les sorties IA de TropiRAG pendant l'investigation
clinique ? Trois simulations en un script :

  1. CALendRIER — R5→R8 (plan de validation v1.0.0) : fenêtres, phase
     active, verdict du garde de décision (451 tant que le CE manque).
  2. COHORTE — inclusions eCRF, monitoring, sûreté (DSMB) : l'instrument
     de mesure vit, les sorties IA restent non décisionnelles.
  3. --LIVE — vérification sur le service réel (:8304) : tampon
     `governance` dans une analyse, garde 451, état public /governance.

Usage :  python scripts/dev/simulate_governance_timeline.py [--live] [--m0 YYYY-MM-DD]
Sortie : console (tableaux texte) — idempotent, aucun écrit disque.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tropirag" / "src"))

from tropirag.governance.investigation import (  # noqa: E402
    add_months,
    default_m0,
    m18_status,
)

# --- fenêtres du plan de validation v1.0.0 (mois M+ de ouverture/clôture) ---
FENETRES = [
    ("R5", 2, 6, "Protocole + soumissions (ANOC-CI, PACTR, Ministère)"),
    ("R6", 6, 18, "Inclusions + monitoring → VERROU DE BASE M+18"),
    ("R7", 18, 21, "Rapport clinique MEDDEV 2.7/1 rev 4 — bénéfice-risque"),
    ("R8", 21, 31, "Notifié + audit + marquage CE (art. 52-54)"),
]

TARGET_SUJETS = 240  # taille d'échantillon du protocole (simulation)


def fenetre_de(mois: int) -> tuple[str, str]:
    for jalon, a, b, _ in FENETRES:
        if a <= mois < b or (jalon == "R8" and mois == b):
            return jalon, ""
    return "—", ""


def phase_verdict(mois: int) -> tuple[str, str]:
    """Verdict du garde de décision pour un mois donné (réplique la logique
    serveur : `certified` exige CE + double opt-in — jamais simulé ici)."""
    if mois < 18:
        return "R6 — investigation ouverte", "451 interdit"
    if mois < 21:
        return "R7 — analyse après verrou de base", "451 interdit"
    if mois < 26:
        return "R8 — notifié, audit en cours", "451 interdit"
    if mois < 31:
        return "R8 — CE attendu (décision humaine)", "451 (jusqu'au CE)"
    return "post-étude", "451 sans double opt-in CE"


def sim_calendrier(m0: date, today: date) -> None:
    m18 = add_months(m0, 18)
    print("=" * 78)
    print("SIMULATION 1 — Calendrier d'investigation R5→R8 (verrou M+18)")
    print(f"  M0 = {m0.isoformat()} · verrou de base M+18 = {m18.isoformat()}"
          f" · aujourd'hui = {today.isoformat()}")
    st = m18_status(today, m0)
    print(f"  aujourd'hui → M+{st['mois_ecoules']} · phase {st['phase_active']}"
          f" · J−{st['jours_avant_verrou']} avant le verrou · décision clinique "
          f"{st['decision_clinique'].upper()}")
    print("-" * 78)
    entete = f"{'Mois':<6}{'Date':<13}{'Phase':<34}{'Garde décision':<20}"
    print(entete)
    print("-" * 78)
    for mois in range(0, 32):
        d = add_months(m0, mois)
        phase, garde = phase_verdict(mois)
        marque = "  ← AUJOURD'HUI" if d.year == today.year and d.month == today.month else ""
        marque = marque or ("  ← VERROU M+18" if d == m18 else "")
        jalon = fenetre_de(mois)[0]
        print(f"M+{mois:<3}{d.isoformat():<13}[{jalon}] {phase:<31}{garde:<20}{marque}")
    print("-" * 78)
    print("  Sortie du régime : marquage CE effectif (R8) + double opt-in serveur")
    print("  (MEDISUITE_GOVERNANCE_MODE=certified ET MEDISUITE_GOVERNANCE_CE_ACK=ce).")
    print("  Sans CE, même après M+18 : toute décision clinique reste interdite (451).")


def sim_cohorte(m0: date, today: date) -> None:
    """Inclusions/monitoring/sûreté — rampe déterministe (pas d'aléatoire :
    simulation reproductible pour les revues DSMB)."""
    print()
    print("=" * 78)
    print("SIMULATION 2 — Cohorte eCRF (instrument de mesure) + sûreté DSMB")
    print(f"  cible protocole : {TARGET_SUJETS} sujets · 4 sites (CHU Cocody, Yopougon,"
          " Bouaké, Dabou)")
    print("-" * 78)
    rampes = [3, 6, 9, 12, 15, 18, 21, 24]  # paliers mensuels d'inclusion
    total = 0
    ei = sae = 0
    requetes = 0
    mois_ecoules = m18_status(today, m0)["mois_ecoules"]
    limite = min(mois_ecoules, 30)
    print(f"{'Mois':<6}{'Inclus (mois)':<15}{'Cumul':<8}{'Requêtes SDV':<14}"
          f"{'EI/SAE':<10}{'Verdict sorties IA'}")
    print("-" * 78)
    for mois in range(3, limite + 1):
        if mois <= 18:
            n = min(rampes[min(mois // 3, len(rampes) - 1)], TARGET_SUJETS - total)
        else:
            n = 0  # verrou de base posé → aucune écriture eCRF (409)
        total += n
        requetes = max(0, requetes + (2 if n else -1))
        # EI liés au dispositif : ~1.2 % des inclusions ; SAE ~0.4 % (borné)
        ei += round(n * 0.012)
        sae += round(n * 0.004)
        _, garde = phase_verdict(mois)
        verdict = "sorties consultables, décision 451" if "451" in garde else "—"
        print(f"M+{mois:<3}{n:<15}{total:<8}{requetes:<14}"
              f"{ei}/{sae:<8}{verdict}")
    print("-" * 78)
    print(f"  aujourd'hui (M+{limite}) : {total}/{TARGET_SUJETS} sujets —"
          f" verrou eCRF {'POSÉ' if m18_status(today, m0)['pose'] else 'non posé'}"
          f" · règle d'arrêt DSMB : 2 SAE inattendus liés au dispositif")
    print("  Les agrégats DSMB alimentent le rapport clinique (R7) — jamais")
    print("  une décision clinique temps réel : les sorties IA restent d'investigation.")


def sim_live(m0: date) -> int:
    base = "http://127.0.0.1:8304"
    print()
    print("=" * 78)
    print("SIMULATION 3 — Service RÉEL (:8304) : tampon + garde 451 + état public")
    print("-" * 78)
    code = 0
    try:
        req = urllib.request.Request(f"{base}/api/v1/governance")
        with urllib.request.urlopen(req, timeout=5) as r:
            etat = json.loads(r.read())
        cal = etat["calendrier"]
        print(f"[1] GET /api/v1/governance          → statut={etat['statut']}"
              f" · verrou={etat['verrou']}"
              f" · décision={etat['decision_clinique']}")
        print(f"    calendrier : M0={cal['m0']} · M+18={cal['verrou_m18']}"
              f" · pose={cal['pose']} · phase={cal['phase_active']}"
              f" · J−{cal['jours_avant_verrou']}")
    except Exception as e:  # noqa: BLE001
        print(f"[1] GET /governance INDISPONIBLE ({e}) — service démarré ?")
        code = 1

    payload = {
        "patient": {"age_years": 34, "sex": "male"},
        "free_text": "fièvre 39,6 depuis 4 jours, frissons, céphalées",
        "travel": {"segments": [{"country": "CI", "rural_stay": True,
                                  "departure": "2026-09-06"}]},
        "vitals": {"temperature_c": 39.6},
    }
    try:
        req = urllib.request.Request(
            f"{base}/api/v1/clinical/analyze", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read())
            g = body.get("governance", {})
            print(f"[2] POST /clinical/analyze          → HTTP {r.status}"
                  f" · tampon governance présent={bool(g)}"
                  f" · statut={g.get('statut')} · décision={g.get('decision_clinique')}")
            print(f"    X-Governance-Lock={r.headers.get('X-Governance-Lock')}"
                  f" · avis='{g.get('avis', '')[:60]}…'")
            if not g or g.get("decision_clinique") != "interdite":
                code = 1
    except Exception as e:  # noqa: BLE001
        print(f"[2] POST /clinical/analyze ÉCHEC ({e})")
        code = 1

    try:
        req = urllib.request.Request(
            f"{base}/api/v1/decision/finalize",
            data=json.dumps({"case_id": "SIM-451", "decision": "hospitalisation"}).encode(),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                print(f"[3] POST /decision/finalize        → HTTP {r.status} — "
                      "ANOMALIE : la garde n'a pas bloqué !")
                code = 1
        except urllib.error.HTTPError as e:
            denial = json.loads(e.read()).get("detail", {})
            ok = e.code == 451 and denial.get("error") == "clinical_decision_locked"
            print(f"[3] POST /decision/finalize        → HTTP {e.code} {e.reason}"
                  f" · error={denial.get('error')}"
                  f" · reprise='{denial.get('reprise')}'"
                  f" · {'VERROU CONFIRMÉ' if ok else 'ANOMALIE'}")
            if not ok:
                code = 1
    except Exception as e:  # noqa: BLE001
        print(f"[3] POST /decision/finalize ÉCHEC ({e})")
        code = 1
    print("-" * 78)
    print("Verdict live : sorties tamponnées « investigation », décision clinique")
    print("matérialisée = 451 Unavailable For Legal Reasons — le verrou M+18 s'applique.")
    return code


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="vérifier aussi le service réel :8304")
    ap.add_argument("--m0", default=None, help="jalon M0 (ISO, défaut : env/sim 2025-06-01)")
    args = ap.parse_args()

    m0 = date.fromisoformat(args.m0) if args.m0 else default_m0()
    today = date.today()

    sim_calendrier(m0, today)
    sim_cohorte(m0, today)
    if args.live:
        return sim_live(m0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
