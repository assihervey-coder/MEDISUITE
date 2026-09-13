"""UDI-EID GS1 — identifiants du dispositif (MDR 2017/745 Annexe I §23.2,
règlement UDI 2019/320). v0.7.

Implémente côté logiciel ce qui est codifiable de la chaîne UDI ; ce qui
relève du terrain est explicitement marqué 🔴 dans labeling.json :
- GTIN-13/14 avec clé de contrôle mod-10 (GS1 General Specifications) ;
- Application Identifiers (01 GTIN, 10 lot, 11 production, 17 expiration,
  21 série) et leur séparation FNC1 (caractère GS 0x1D) ;
- GS1 Digital Link (URI id.gs1.org) pour l'EID — entrepôt d'identification
  électronique consultable depuis l'étiquette ;
- Basic UDI-DI dérivé du GTIN de base (emballage niveau 0) ;
- composition de l'élément-string à imprimer en DataMatrix.

Agence émettrice : GS1 (GS1 Côte d'Ivoire) — l'attribution réelle du préfixe
entreprise et l'impression des étiquettes restent des jalons terrain (R8).
Zéro dépendance, fonctions pures.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any

# ── Application Identifiers utilisés par MEDISUITE ───────────────────────────

AI = {
    "GTIN": "01",          # Global Trade Item Number (14 digits, fixe)
    "LOT": "10",           # numéro de lot (variable, ≤ 20)
    "PROD_DATE": "11",     # date de production YYMMDD (fixe)
    "EXPIRY": "17",        # date d'expiration YYMMDD (fixe)
    "SERIAL": "21",        # numéro de série (variable, ≤ 20)
}

FNC1 = "\x1d"  # Group Separator : terminateur des AIs de longueur variable

# AI 10/21 : jeu ISO/IEC 646 restreint documenté (chiffres, lettres, .-/+/%)
_VAR_AI_RE = re.compile(r"^[A-Za-z0-9._/\-+%]{1,20}$")
_GTIN_RE = re.compile(r"^\d{13,14}$")
_GS1_DATE_RE = re.compile(r"^\d{6}$")

# Émetteur d'identification (EID) : statut honnête — proposition GS1,
# adhésion à finaliser (jalon R8 du plan v1.0.0).
ISSUING_ENTITY = {
    "agence": "GS1 Côte d'Ivoire",
    "role": "organisme émetteur d'UDI (MDR art. 27, règlement 2019/320)",
    "statut": "proposé — adhésion 🔴 terrain (jalon R8)",
}

# GTIN de base (niveau emballage 0) proposé pour MEDISUITE plateforme.
# Préfixe entreprise de démonstration : NE PAS PRODUIRE avant attribution
# GS1 réelle (l'adhésion GS1 CI attribuera le préfixe définitif — jalon R8).
DEMO_GS1_PREFIX = "260"   # préfixe CI (GS1 CI) — à confirmer par l'adhésion
DEMO_GTN_BASE_12 = DEMO_GS1_PREFIX + "000000001"  # 12 chiffres de données


class Gs1UdiError(ValueError):
    """Élément-string UDI GS1 invalide."""


# ── GTIN (AI 01) ─────────────────────────────────────────────────────────────

def gtin_check_digit(data_digits: str) -> str:
    """Clé de contrôle GS1 mod-10 sur 12 chiffres (GTIN-13) ou 13 (GTIN-14)
    de données, poids 3/1 de droite à gauche."""
    base = (data_digits or "").strip()
    if not re.match(r"^\d{12,13}$", base):
        raise Gs1UdiError(f"base GTIN invalide : '{data_digits}' (12 chiffres "
                          "pour GTIN-13, 13 pour GTIN-14)")
    total = 0
    for i, ch in enumerate(reversed(base)):
        total += int(ch) * (3 if i % 2 == 0 else 1)
    return str((10 - (total % 10)) % 10)


def build_gtin14(data13: str) -> str:
    """GTIN-14 complet : 13 chiffres de données (dont indicateur d'emballage)
    + clé de contrôle recalculée."""
    base = (data13 or "").strip()
    if not re.match(r"^\d{13}$", base):
        raise Gs1UdiError(f"données GTIN-14 invalides : '{data13}' "
                          "(13 chiffres attendus, indicateur inclus)")
    return base + gtin_check_digit(base)


def validate_gtin(gtin: str) -> str:
    """Vérifie un GTIN-13/14 (longueur + clé de contrôle). Fail-closed."""
    g = (gtin or "").strip()
    if not _GTIN_RE.match(g):
        raise Gs1UdiError(f"GTIN invalide : '{gtin}' (13-14 chiffres)")
    key = g[-1]
    expected = gtin_check_digit(g[:-1])
    if key != expected:
        raise Gs1UdiError(f"clé de contrôle GTIN invalide : attendue "
                          f"'{expected}', trouvée '{key}'")
    return g


def basic_udi_di(base12: str = DEMO_GTN_BASE_12) -> str:
    """Basic UDI-DI GS1 = GTIN-14 d'indicateur d'emballage « 0 ».

    Identifie le MODÈLE (pas l'unité) — c'est l'identifiant porté au
    dossier technique et à EUDAMED. Statut : 🔴 à émettre par GS1 (R8).
    `base12` = 12 chiffres de données (préfixe GS1 + référence modèle).
    """
    base = (base12 or "").strip()
    if not re.match(r"^\d{12}$", base):
        raise Gs1UdiError(f"base Basic UDI-DI invalide : '{base12}' "
                          "(12 chiffres de données attendus)")
    return build_gtin14("0" + base)


# ── Dates GS1 (AI 11 / 17, YYMMDD — jour 00 = « jour inconnu ») ─────────────

def fmt_gs1_date(value: str) -> str:
    """'2026-09-14' → '260914' (jour 00 accepté pour « fin de mois »)."""
    v = (value or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", v)
    if not m:
        raise Gs1UdiError(f"date ISO attendue (AAAA-MM-JJ) : '{value}'")
    y, mo, d = m.groups()
    if not 1 <= int(mo) <= 12 or not 0 <= int(d) <= 31:
        raise Gs1UdiError(f"date hors bornes : '{value}'")
    return f"{y[2:]}{mo}{d}"


def parse_gs1_date(value: str) -> date:
    """'260914' → date(2026, 9, 14) ; jour '00' → dernier jour du mois."""
    v = (value or "").strip()
    if not _GS1_DATE_RE.match(v):
        raise Gs1UdiError(f"date GS1 YYMMDD attendue : '{value}'")
    yy, mo, dd = int(v[0:2]), int(v[2:4]), int(v[4:6])
    if not 1 <= mo <= 12 or dd > 31:
        raise Gs1UdiError(f"date GS1 hors bornes : '{value}'")
    year = 2000 + yy
    if dd == 0:  # convention GS1 : 00 = jour inconnu → fin de mois
        if mo == 12:
            return date(year, 12, 31)
        return date(year, mo + 1, 1) - timedelta(days=1)
    try:
        return date(year, mo, dd)
    except ValueError as exc:
        raise Gs1UdiError(f"date GS1 inexistante : '{value}' ({exc})")


# ── Élément-string (contenu DataMatrix) ──────────────────────────────────────

def _check_var(value: str, ai: str) -> str:
    v = (value or "").strip()
    if not _VAR_AI_RE.match(v):
        raise Gs1UdiError(f"AI ({ai}) invalide : '{value}' (≤ 20 caractères "
                          "alphanumériques .-/+%)")
    return v


def build_element_string(gtin: str, lot: str = "",
                         expiry: str = "", prod: str = "",
                         serial: str = "") -> str:
    """Compose l'élément-string UDI (ce que le DataMatrix encodera).

    Ordre GS1 : (01) puis (17) puis (11) puis (10) puis (21). Les AIs à
    longueur fixe (01/11/17) ne sont jamais terminés ; les AIs variables
    (10/21) reçoivent FNC1 sauf s'ils sont en dernière position.
    """
    g = validate_gtin(gtin)
    g14 = g if len(g) == 14 else "0" + g
    segments: list[str] = [AI["GTIN"] + g14]
    if expiry:
        segments.append(AI["EXPIRY"] + fmt_gs1_date(expiry))
    if prod:
        segments.append(AI["PROD_DATE"] + fmt_gs1_date(prod))
    if lot:
        segments.append(AI["LOT"] + _check_var(lot, AI["LOT"]))
    if serial:
        segments.append(AI["SERIAL"] + _check_var(serial, AI["SERIAL"]))
    out: list[str] = []
    for idx, seg in enumerate(segments):
        variable = seg[:2] in (AI["LOT"], AI["SERIAL"])
        last = idx == len(segments) - 1
        out.append(seg + (FNC1 if variable and not last else ""))
    return "".join(out)


def parse_element_string(element: str) -> dict[str, str]:
    """Décompose un élément-string GS1 en {AI: valeur} avec validation."""
    out: dict[str, str] = {}
    s = (element or "").strip()
    if not s:
        raise Gs1UdiError("élément-string vide")
    i = 0
    while i < len(s):
        ai = s[i:i + 2]
        i += 2
        if ai == AI["GTIN"]:
            out[ai] = s[i:i + 14]
            validate_gtin(out[ai])
            i += 14
        elif ai in (AI["PROD_DATE"], AI["EXPIRY"]):
            raw = s[i:i + 6]
            parse_gs1_date(raw)
            out[ai] = raw
            i += 6
        elif ai in (AI["LOT"], AI["SERIAL"]):
            end = s.find(FNC1, i)
            if end == -1:
                out[ai] = s[i:]
                i = len(s)
            else:
                out[ai] = s[i:end]
                i = end + 1
            _check_var(out[ai], ai)
        else:
            raise Gs1UdiError(f"AI inconnu ou non supporté : '({ai})'")
    if AI["GTIN"] not in out:
        raise Gs1UdiError("AI (01) GTIN obligatoire et en tête")
    return out


# ── GS1 Digital Link (EID — entrepôt d'identification électronique) ─────────

def gs1_digital_link(gtin: str, lot: str = "", serial: str = "",
                     domain: str = "https://id.gs1.org") -> str:
    """URI GS1 Digital Link : l'étiquette pointe vers l'EID du fabricant.

    https://id.gs1.org/01/{gtin}/10/{lot}/21/{serial} — le résolveur GS1
    redirige vers l'entrepôt de données du fabricant (EID).
    """
    g = validate_gtin(gtin)
    path = f"/01/{g}"
    if lot:
        path += f"/10/{_check_var(lot, AI['LOT'])}"
    if serial:
        path += f"/21/{_check_var(serial, AI['SERIAL'])}"
    return domain.rstrip("/") + path


# ── Étiquette complète (MDR Annexe I §23.2) ──────────────────────────────────

def label_payload(gtin: str, lot: str = "", expiry: str = "",
                  prod: str = "", serial: str = "",
                  version_logiciel: str = "",
                  basic_udi: str = "") -> dict[str, Any]:
    """Toutes les composantes d'étiquetage UDI d'une unité installée."""
    return {
        "basic_udi_di": basic_udi or basic_udi_di(),
        "udi_di": validate_gtin(gtin),
        "element_string": build_element_string(gtin, lot=lot, expiry=expiry,
                                               prod=prod, serial=serial),
        "digital_link": gs1_digital_link(gtin, lot=lot, serial=serial),
        "application_identifiers": {k: f"({v})" for k, v in AI.items()},
        "lot": lot or None,
        "date_production": fmt_gs1_date(prod) if prod else None,
        "date_expiration": fmt_gs1_date(expiry) if expiry else None,
        "serie": serial or None,
        "version_logiciel": version_logiciel or None,
        "emetteur": ISSUING_ENTITY,
        "reglementaire": "MDR 2017/745 Annexe I §23.2 + règlement UDI 2019/320",
    }


def verify_label_payload(payload: dict[str, Any]) -> tuple[bool, str | None]:
    """Vérifie un élément-string affiché : GTIN + dates + AIs cohérents."""
    try:
        parsed = parse_element_string(payload.get("element_string", ""))
    except Gs1UdiError as exc:
        return False, str(exc)
    if payload.get("lot") and parsed.get(AI["LOT"]) != payload["lot"]:
        return False, "lot de l'étiquette ≠ élément-string"
    if payload.get("serie") and parsed.get(AI["SERIAL"]) != payload["serie"]:
        return False, "série de l'étiquette ≠ élément-string"
    return True, None
