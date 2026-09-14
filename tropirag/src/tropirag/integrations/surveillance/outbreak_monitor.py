"""Moniteur d'éclosions — agrégation géographique des cas persistés (V1.3).

Cartographie des éclosions de fièvre+voyage par district sanitaire de Côte
d'Ivoire (14 districts de 1er niveau — cohérents avec les unités
d'organisation DHIS2 de configs/integrations/dhis2.yaml).

    analyses persistées (SQLite)
        → district résolu depuis le segment CI du voyage (région déclarée)
        → agrégats par district : cas, suspicions par maladie, urgences,
          courbe hebdomadaire
        → clusters d'éclosion : augmentation vs semaine précédente

DÉTERMINISME INTÉGRAL : seules les analyses du moteur de règles sont
comptées (table ``analyses``) — l'IA ne participe jamais au comptage
(agrégeable avec l'export DHIS2, même source de vérité).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Districts sanitaires de Côte d'Ivoire (14 districts de 1er niveau)
# grid : position approximative (colonne, ligne) pour la carte schématique
# aligné sur la géographie réelle (ligne 0 = nord).
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class District:
    key: str
    label: str                 # nom du district
    chief_town: str            # ville principale
    grid: tuple[int, int]      # (colonne, ligne) pour le rendu schématique


CI_DISTRICTS: dict[str, District] = {
    d.key: d for d in [
        District("denguele",         "Denguélé",          "Odienné",        (0, 0)),
        District("savanes",          "Savanes",           "Korhogo",        (1, 0)),
        District("zanzan",           "Zanzan",            "Bondoukou",      (2, 0)),
        District("worodougou",        "Worodougou",         "Séguéla",        (0, 1)),
        District("vallee-du-bandama", "Vallée du Bandama",  "Bouaké",         (1, 1)),
        District("indenie-djuablin",  "Indénié-Djuablin",   "Abengourou",     (2, 1)),
        District("montagnes",        "Montagnes",          "Man",            (0, 2)),
        District("sassandra-marahoue", "Sassandra-Marahoué", "Daloa",      (1, 2)),
        District("lacs",             "Lacs",               "Dimbokro",       (2, 2)),
        District("bas-sassandra",    "Bas-Sassandra",      "San-Pédro",      (0, 3)),
        District("goh-djiboua",      "Gôh-Djiboua",        "Gagnoa",         (1, 3)),
        District("abidjan",          "District d'Abidjan", "Abidjan",        (2, 3)),
        District("comoe",            "Comoé",              "Aboisso",        (3, 3)),
        District("yamoussoukro",     "District de Yamoussoukro", "Yamoussoukro", (3, 2)),
    ]
}

# Régions/préfectures usuelles → district (normalisation accents/insensible casse).
_REGION_TO_DISTRICT: dict[str, str] = {
    # Abidjan
    "abidjan": "abidjan", "district d abidjan": "abidjan",
    # Yamoussoukro
    "yamoussoukro": "yamoussoukro", "district de yamoussoukro": "yamoussoukro",
    # Bas-Sassandra
    "san pedro": "bas-sassandra", "sassandra": "bas-sassandra",
    "tabou": "bas-sassandra", "soubre": "bas-sassandra", "soubré": "bas-sassandra",
    "fresco": "bas-sassandra", "grabo": "bas-sassandra", "meagui": "bas-sassandra",
    # Comoé
    "aboisso": "comoe", "aboisso": "comoe", "grand bassam": "comoe",
    "grand-bassam": "comoe", "bonoua": "comoe", "sud comoe": "comoe",
    "sud-comoe": "comoe", "comoe": "comoe", "adike": "comoe",
    # Denguélé
    "odienné": "denguele", "odienné": "denguele", "madinani": "denguele",
    "minignan": "denguele", "gbéléban": "denguele",
    # Gôh-Djiboua
    "gagnoa": "goh-djiboua", "oume": "goh-djiboua", "oumé": "goh-djiboua",
    "lakota": "goh-djiboua", "divo": "goh-djiboua", "goh": "goh-djiboua",
    "djiboua": "goh-djiboua",
    # Indénié-Djuablin
    "abengourou": "indenie-djuablin", "agnibilekrou": "indenie-djuablin",
    "agnibilékrou": "indenie-djuablin", "bongouanou": "indenie-djuablin",
    "indenié": "indenie-djuablin", "indenie": "indenie-djuablin",
    # Lacs
    "dimbokro": "lacs", "toumodi": "lacs", "toumodi": "lacs",
    "daoukro": "lacs", "ndouci": "lacs", "arrah": "lacs",
    # Montagnes
    "man": "montagnes", "danane": "montagnes", "danané": "montagnes",
    "bangolo": "montagnes", "bangolo": "montagnes", "coulibaly": "montagnes",
    "sipilou": "montagnes", "biankouma": "montagnes",
    # Sassandra-Marahoué
    "daloa": "sassandra-marahoue", "issia": "sassandra-marahoue",
    "zuenoula": "sassandra-marahoue", "zuénoula": "sassandra-marahoue",
    "vavoua": "sassandra-marahoue", "marahoue": "sassandra-marahoue",
    "bonon": "sassandra-marahoue",
    # Savanes
    "korhogo": "savanes", "boundiali": "savanes", "tingrela": "savanes",
    "tingréla": "savanes", "m'bengue": "savanes", "dianra": "savanes",
    # Vallée du Bandama
    "bouake": "vallee-du-bandama", "bouaké": "vallee-du-bandama",
    "katiola": "vallee-du-bandama", "beoumi": "vallee-du-bandama",
    "béoumi": "vallee-du-bandama", "sakassou": "vallee-du-bandama",
    "botro": "vallee-du-bandama",
    # Worodougou
    "seguéla": "worodougou", "seguela": "worodougou", "seguéla": "worodougou",
    "mankono": "worodougou", "kani": "worodougou",
    # Zanzan
    "bondoukou": "zanzan", "bouna": "zanzan", "tanda": "zanzan",
    "tandounde": "zanzan", "kounahiri": "zanzan",
}


def _norm_region(r: str) -> str:
    t = r.lower().strip()
    t = re.sub(r"[-_]", " ", t)
    t = re.sub(r"\s+", " ", t)
    # suppression des accents (NFKD)
    import unicodedata

    t = "".join(c for c in unicodedata.normalize("NFKD", t)
                if not unicodedata.combining(c))
    return t


def resolve_district(region: str | None) -> str | None:
    """Région déclarée → clé de district CI ; None si hors correspondance."""
    if not region:
        return None
    n = _norm_region(region)
    if n in _REGION_TO_DISTRICT:
        return _REGION_TO_DISTRICT[n]
    # correspondance par nom de district directement
    for key, d in CI_DISTRICTS.items():
        if n == _norm_region(d.label) or n == _norm_region(d.chief_town):
            return key
    # préfixe : « district de daloa », « région korhogo » ...
    for n2 in (n.replace("district de ", "").replace("district d ", ""),
               n.replace("region de ", "").replace("region d ", "")):
        if n2 in _REGION_TO_DISTRICT:
            return _REGION_TO_DISTRICT[n2]
    return None


# ---------------------------------------------------------------------------
# Cluster d'éclosion
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class DistrictCluster:
    key: str
    cases: int = 0
    urgent: int = 0
    critical: int = 0
    by_disease: dict[str, int] = field(default_factory=dict)
    by_week: dict[str, int] = field(default_factory=dict)
    last_case_at: str | None = None

    def to_dict(self) -> dict:
        d = CI_DISTRICTS[self.key]
        return {
            "key": self.key,
            "label": d.label,
            "chief_town": d.chief_town,
            "cases": self.cases,
            "urgent": self.urgent,
            "critical": self.critical,
            "by_disease": dict(sorted(self.by_disease.items(),
                                      key=lambda kv: -kv[1])[:8]),
            "by_week": dict(sorted(self.by_week.items())),
            "last_case_at": self.last_case_at,
        }


class OutbreakMonitor:
    """Agrège les analyses persistées en signaux d'éclosion par district CI.

    Le district provient du segment de voyage en Côte d'Ivoire (champ
    ``region`` — saisie PWA mobile ou API). Les cas sans district résolu
    tombent dans le compartiment ``non_localises`` (toujours comptés dans
    le total national — jamais silencieusement perdus).
    """

    def __init__(self, db) -> None:  # tropirag.persistence.database.Database
        self.db = db

    # ------------------------------------------------------------------
    def _rows(self, days: int) -> list[dict]:
        import datetime as dt

        start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
        rows = self.db.query(
            "SELECT a.*, c.payload_json AS payload_json FROM analyses a "
            "LEFT JOIN cases c ON c.case_id = a.case_id "
            "WHERE a.created_at >= ? ORDER BY a.id", (start,))
        return [dict(r) for r in rows]

    def _district_of(self, payload_json: str | None) -> str | None:
        if not payload_json:
            return None
        try:
            payload = json.loads(payload_json)
        except (json.JSONDecodeError, TypeError):
            return None
        for seg in (payload.get("travel") or {}).get("segments") or []:
            seg = seg if isinstance(seg, dict) else {}
            if str(seg.get("country", "")).upper() in ("CI", "CIV"):
                district = resolve_district(seg.get("region"))
                if district:
                    return district
        return None

    # ------------------------------------------------------------------
    def clusters(self, days: int = 30) -> dict:
        """Snapshot d'éclosion : districts + total national + compartiments."""
        from collections import Counter

        rows = self._rows(days)
        per_district: dict[str, DistrictCluster] = {}
        non_localises = DistrictCluster(key="__non_localises__")
        total = Counter()

        for row in rows:
            diseases = self._diseases(row)
            urgent = str(row.get("urgency")) in ("emergency", "immediate")
            critical = str(row.get("severity")) == "critical"
            week = _iso_week(str(row.get("created_at", "")))
            key = self._district_of(row.get("payload_json"))

            cluster = per_district.setdefault(key, DistrictCluster(key)) \
                if key else non_localises
            cluster.cases += 1
            cluster.urgent += int(urgent)
            cluster.critical += int(critical)
            cluster.by_week[week] = cluster.by_week.get(week, 0) + 1
            cluster.last_case_at = max(cluster.last_case_at or "",
                                       str(row.get("created_at", "")))
            for disease in diseases:
                cluster.by_disease[disease] = cluster.by_disease.get(disease, 0) + 1
            total.update(diseases)

        # signaux d'éclosion : progression de la dernière semaine vs précédente
        outbreaks = []
        for key, c in per_district.items():
            weeks = sorted(c.by_week)
            if len(weeks) >= 2:
                last, prev = c.by_week[weeks[-1]], c.by_week[weeks[-2]]
                if last >= prev + 2 and last >= 3:  # +2 cas minimum, seuil épidémique
                    outbreaks.append({
                        "district": key, "label": CI_DISTRICTS[key].label,
                        "last_week": weeks[-1], "cases_last_week": last,
                        "cases_previous_week": prev,
                        "top_disease": max(c.by_disease, key=c.by_disease.get)
                        if c.by_disease else None,
                    })

        return {
            "window_days": days,
            "total_cases": len(rows),
            "national_by_disease": dict(sorted(total.items(),
                                               key=lambda kv: -kv[1])),
            "districts": [per_district[k].to_dict()
                          for k in sorted(per_district)],
            "non_localises": {
                "cases": non_localises.cases,
                "urgent": non_localises.urgent,
                "by_disease": dict(sorted(non_localises.by_disease.items(),
                                          key=lambda kv: -kv[1])),
            },
            "outbreaks": sorted(outbreaks, key=lambda o: -o["cases_last_week"]),
            "districts_meta": [
                {"key": d.key, "label": d.label, "chief_town": d.chief_town,
                 "grid": list(d.grid)}
                for d in CI_DISTRICTS.values()
            ],
        }

    @staticmethod
    def _diseases(row: dict) -> list[str]:
        try:
            diffs = json.loads(row.get("differentials_json") or "[]")
        except (json.JSONDecodeError, TypeError):
            return []
        return [str(d.get("disease")) for d in diffs
                if not d.get("excluded")]


def _iso_week(created_at: str) -> str:
    """'2026-09-12T10:00:00' → '2026W37' (vide si date illisible)."""
    try:
        from datetime import datetime

        d = datetime.fromisoformat(created_at[:19])
        iso = d.isocalendar()
        return f"{iso.year}W{iso.week:02d}"
    except (ValueError, TypeError):
        return "?"
