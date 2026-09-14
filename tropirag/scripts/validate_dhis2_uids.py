#!/usr/bin/env python3
"""Validateur de correspondance DHIS2 — MSP-CI / TropiRAG.

Vérifie que configs/integrations/dhis2.yaml est prêt pour la correspondance
officielle avec le dictionnaire de données DHIS2 national (MSP-CI) :

  1. chaque UID suit le format DHIS2 (^[A-Za-z][A-Za-z0-9]{10}$) ;
  2. les placeholders provisoires (DE-TRPG-*, DS-TRPG-*, COC-TRPG-*, OU-TRPG-*)
     sont listés et comptés — ils doivent être remplacés avant tout push ;
  3. les clés logiques attendues par le code sont toutes présentes (aucune
     régression du mapping) ;
  4. le serveur / identifiants sont configurés si le mode « push » est demandé.

Usage :
    python scripts/validate_dhis2_uids.py             # rapport lisible
    python scripts/validate_dhis2_uids.py --strict    # exit 1 si non prêt
    python scripts/validate_dhis2_uids.py --json      # sortie machine
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.integrations.dhis2.settings import (  # noqa: E402
    DEFAULT_CONFIG_PATH,
    Dhis2Config,
)

# UID DHIS2 : 11 caractères, premier alphabétique, alphanumériques ensuite.
UID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{10}$")
PLACEHOLDER_RE = re.compile(r"^(?:DE|DS|COC|OU)-TRPG-", re.IGNORECASE)

# Clés logiques que le mapper considère comme définies dans le YAML —
# toute disparition est une régression bloquante.
EXPECTED_ELEMENTS = [
    "total_cases", "suspect_malaria", "suspect_severe_malaria",
    "malaria_renal_rrt", "suspect_dengue", "suspect_severe_dengue",
    "dengue_peds_critical", "suspect_enteric_fever", "typhoid_xdr",
    "suspect_yellow_fever", "suspected_vhf", "suspect_leptospirosis",
    "suspect_meningococcal", "suspect_zika", "zika_pregnant",
    "scd_fever", "pregnancy_malaria", "urgent_cases", "critical_cases",
]


def classify(uid: str) -> str:
    """'valide' | 'placeholder' | 'invalide'."""
    if PLACEHOLDER_RE.match(uid or ""):
        return "placeholder"
    return "valide" if UID_RE.match(uid or "") else "invalide"


def validate(cfg: Dhis2Config, raw_yaml: dict) -> dict:
    dhis2 = raw_yaml.get("dhis2") or {}
    report: dict = {
        "config": str(DEFAULT_CONFIG_PATH),
        "elements": {}, "org_units": {}, "data_sets": {}, "cocs": {},
        "counts": {"valide": 0, "placeholder": 0, "invalide": 0},
        "regressions": [], "erreurs": [], "pret_push": False,
    }

    # — éléments de données ————————————————————————————————————————
    for key, spec in sorted(cfg.data_elements.items()):
        status = classify(spec.de)
        report["elements"][key] = {
            "uid": spec.de, "status": status, "label": spec.label,
            "definition": str((raw_yaml.get("data_elements") or {})
                              .get(key, {}).get("definition", "")),
        }
        report["counts"][status] += 1
    for key in EXPECTED_ELEMENTS:
        if key not in report["elements"]:
            report["regressions"].append(
                f"clé logique absente du YAML : {key} (régression mapping)")

    # — unités d'organisation ————————————————————————————————————
    ou = dhis2.get("organisation_unit") or {}
    default_ou = str(ou.get("default", ""))
    report["org_units"]["default"] = {
        "uid": default_ou, "status": classify(default_ou),
        "label": str(ou.get("label", ""))}
    report["counts"][classify(default_ou)] += 1
    for key, spec in (ou.get("units") or {}).items():
        uid = str((spec or {}).get("ou", ""))
        status = classify(uid)
        report["org_units"][key] = {"uid": uid, "status": status,
                                    "label": str((spec or {}).get("label", ""))}
        report["counts"][status] += 1

    # — jeux de données ———————————————————————————————————————————
    for key, spec in (dhis2.get("data_sets") or {}).items():
        uid = str((spec or {}).get("ds", ""))
        status = classify(uid)
        report["data_sets"][key] = {"uid": uid, "status": status,
                                    "label": str((spec or {}).get("label", ""))}
        report["counts"][status] += 1

    # — combos de catégories ———————————————————————————————————————
    for key, uid in (dhis2.get("category_option_combos") or {}).items():
        status = classify(str(uid))
        report["cocs"][key] = {"uid": str(uid), "status": status}
        report["counts"][status] += 1

    # — erreurs bloquantes —————————————————————————————————————————
    for key, info in report["elements"].items():
        if info["status"] == "invalide":
            report["erreurs"].append(
                f"{key} : UID « {info['uid']} » ni placeholder ni format DHIS2 valide")
    if report["regressions"]:
        report["erreurs"].append(f"{len(report['regressions'])} régression(s) mapping")

    # — verdict : prêt pour le push ? ————————————————————————————————
    ready = (
        not report["erreurs"]
        and report["counts"]["placeholder"] == 0
        and report["counts"]["invalide"] == 0
        and cfg.transport_ready
        and cfg.mode == "push"
    )
    report["pret_push"] = ready
    report["transport_ready"] = cfg.transport_ready
    report["mode"] = cfg.mode
    return report


def render_text(report: dict) -> str:
    lines: list[str] = []
    c = report["counts"]
    lines.append("=" * 78)
    lines.append("CORRESPONDANCE DHIS2 — MSP-CI / TropiRAG")
    lines.append(f"Fichier : {report['config']}")
    lines.append("=" * 78)
    lines.append("")

    lines.append("[RÉCAPITULATIF GLOBAL]")
    lines.append(f"  UID valide={c['valide']}  placeholder={c['placeholder']}  "
                 f"invalide={c['invalide']}  (toutes sections confondues)")
    lines.append("")
    lines.append("[ÉLÉMENTS DE DONNÉES]")
    for key, info in report["elements"].items():
        mark = {"valide": "OK ", "placeholder": "…  ", "invalide": "ERR"}[info["status"]]
        lines.append(f"  [{mark}] {key:<24} {info['uid']:<14} {info['label']}")
    lines.append("")
    lines.append("[JEU DE DONNÉES]")
    for key, info in report["data_sets"].items():
        mark = {"valide": "OK ", "placeholder": "…  ", "invalide": "ERR"}[info["status"]]
        lines.append(f"  [{mark}] {key:<24} {info['uid']:<14} {info['label']}")
    lines.append("")
    lines.append("[UNITÉS D'ORGANISATION]")
    for key, info in report["org_units"].items():
        mark = {"valide": "OK ", "placeholder": "…  ", "invalide": "ERR"}[info["status"]]
        lines.append(f"  [{mark}] {key:<24} {info['uid']:<14} {info['label']}")
    lines.append("")
    lines.append("[COMBOS DE CATÉGORIES]")
    for key, info in report["cocs"].items():
        mark = {"valide": "OK ", "placeholder": "…  ", "invalide": "ERR"}[info["status"]]
        lines.append(f"  [{mark}] {key:<24} {info['uid']}")
    lines.append("")

    if report["erreurs"]:
        lines.append("ERREURS BLOQUANTES :")
        for e in report["erreurs"]:
            lines.append(f"  !! {e}")
        lines.append("")
    for r in report["regressions"]:
        lines.append(f"  !! {r}")

    total = c["valide"] + c["placeholder"] + c["invalide"]
    lines.append("-" * 78)
    lines.append(f"Total UIDs : {total} — valide={c['valide']}  "
                 f"placeholder={c['placeholder']}  invalide={c['invalide']}")
    if report["pret_push"]:
        lines.append("VERDICT : PRÊT POUR LE PUSH — tous les UIDs sont officiels "
                     "et le serveur est configuré.")
    elif not report["transport_ready"]:
        lines.append("VERDICT : mode offline_queue actif — placeholders en attente "
                     "de la correspondance MSP-CI (serveur non configuré).")
        lines.append("         Après correspondance : renseigner base_url/username, "
                     "passer dhis2.mode=push, relancer --strict.")
    else:
        lines.append("VERDICT : CORRESPONDANCE INCOMPLÈTE — remplacer les "
                     "placeholders ci-dessus par les UIDs du dictionnaire MSP-CI.")
    lines.append("Procédure : docs/integrations/dhis2-correspondance-msp-ci.md")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validation correspondance DHIS2 MSP-CI")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 si des placeholders/erreurs subsistent")
    ap.add_argument("--json", action="store_true", help="sortie JSON machine")
    args = ap.parse_args()

    import yaml

    p = Path(args.config)
    with open(p, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    cfg = Dhis2Config.from_yaml(p)
    report = validate(cfg, raw)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print(render_text(report))

    not_ready = bool(report["erreurs"]) or report["counts"]["placeholder"] > 0
    if args.strict and not_ready:
        print("\n--strict : correspondance incomplète → échec.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
