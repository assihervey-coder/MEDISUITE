"""Planificateur DHIS2 — export/push hebdomadaire automatique (cron MSP-CI).

Chaque semaine, après la clôture de la semaine ISO, le service exporte les
analyses déterministes de la semaine **écoulée** vers la file DHIS2 puis —
si le mode auto ``push`` est activé et le transport configuré — pousse la
file vers le serveur du MSP-CI.

Configuration (variables d'environnement, exposées par services/registry.py) :
    TROPIRAG_DHIS2_AUTO          off | queue | push   (défaut : off)
    TROPIRAG_DHIS2_PUSH_DAY      MON..SUN             (défaut : MON)
    TROPIRAG_DHIS2_PUSH_HOUR_UTC 0..23                (défaut : 6)

Sécurité :
  - ``off`` (défaut) : aucun envoi automatique — le push reste manuel (UI/CLI) ;
  - ``queue`` : export automatique en file, **aucun appel réseau** ;
  - ``push`` : export + envoi ; si le transport n'est pas prêt (serveur non
    configuré), le payload reste en file — rien n'est perdu, rien n'est inventé.
L'état (dernier envoi, prochain créneau, résultat) est persisté dans
``runtime/state/dhis2_cron.json`` et exposé via l'API (export/dhis2/cron).
"""
from __future__ import annotations

import asyncio
import json
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path

from tropirag.core.datetime import local_now
from tropirag.integrations.dhis2.mapper import period_bounds, period_from_date

_WEEKDAYS = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}
_TICK_S = 60.0


# ---------------------------------------------------------------------------
# Logique pure (testée sans asyncio ni réseau)
# ---------------------------------------------------------------------------
def normalize_day(day: str) -> str:
    d = (day or "MON").strip().upper()[:3]
    if d not in _WEEKDAYS:
        raise ValueError(f"jour inconnu : {day!r} (attendus : {sorted(_WEEKDAYS)})")
    return d


def normalize_hour(hour: int) -> int:
    if not 0 <= int(hour) <= 23:
        raise ValueError(f"heure invalide : {hour} (attendu : 0..23)")
    return int(hour)


def previous_period(now: datetime) -> str:
    """Semaine ISO **écoulée** (YYYYWww) — complète même si on est lundi."""
    return period_from_date((now - timedelta(days=7)).date())


def next_occurrence(now: datetime, day: str, hour: int) -> datetime:
    """Prochain créneau (jour/heures UTC) strictement postérieur à ``now``."""
    target = _WEEKDAYS[normalize_day(day)]
    cand = now.replace(hour=normalize_hour(hour), minute=0, second=0,
                       microsecond=0)
    cand += timedelta(days=(target - cand.weekday()) % 7)
    if cand <= now:
        cand += timedelta(days=7)
    return cand


# ---------------------------------------------------------------------------
# État persisté
# ---------------------------------------------------------------------------
def _state_path() -> Path:
    from tropirag.core.config import TROPIRAG_ROOT

    return TROPIRAG_ROOT / "runtime" / "state" / "dhis2_cron.json"


def load_state() -> dict:
    try:
        with open(_state_path(), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    p = _state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# Orchestrateur
# ---------------------------------------------------------------------------
def config_from_env() -> dict:
    return {
        "auto": (os.environ.get("TROPIRAG_DHIS2_AUTO", "off") or "off").lower(),
        "day": normalize_day(os.environ.get("TROPIRAG_DHIS2_PUSH_DAY", "MON")),
        "hour_utc": normalize_hour(
            os.environ.get("TROPIRAG_DHIS2_PUSH_HOUR_UTC", "6")),
    }


def run_weekly_job(now: datetime | None = None) -> dict:
    """Un cycle complet : export de la semaine écoulée → file (+ push auto).

    Retourne (et persiste) un rapport autonome — l'API et l'UI affichent
    exactement ce dictionnaire. Aucune exception ne s'échappe : un échec
    réseau laisse la file intacte et le rapport rend compte de l'échec.
    """
    now = now or local_now()
    cfg = config_from_env()
    period = previous_period(now)
    report: dict = {"ran_at": now.isoformat(timespec="seconds"),
                    "period": period, "mode": cfg["auto"], "ok": False,
                    "values": 0, "enqueued": False, "pushed": 0,
                    "notes": []}
    if cfg["auto"] == "off":
        report["notes"].append("auto désactivé (TROPIRAG_DHIS2_AUTO=off)")
        return report

    bounds = period_bounds(period)
    from tropirag.persistence.database import Database
    from tropirag.persistence.repositories.case_repository import CaseRepository
    from tropirag.integrations.dhis2.exporter import Dhis2Exporter
    from tropirag.integrations.dhis2.settings import load_dhis2_config

    repo = CaseRepository(Database.instance())
    rows = repo.analyses_between(bounds[0].isoformat(), bounds[1].isoformat())
    exp = Dhis2Exporter(load_dhis2_config())
    result = exp.export(rows, period, enqueue=True)
    report.update({"values": len(result.data_values),
                   "enqueued": result.enqueued,
                   "notes": list(result.notes)})

    if cfg["auto"] == "push":
        if not exp.cfg.transport_ready:
            report["notes"].append(
                "push auto impossible : serveur DHIS2 non configuré "
                "(TROPIRAG_DHIS2_BASE_URL/USERNAME) — payload conservé en file")
        elif result.data_values:
            reports = exp.flush_queue()
            ok = sum(1 for r in reports if r.ok)
            report["pushed"] = ok
            report["ok"] = ok == len(reports) and ok > 0
            report["notes"].append(
                f"push auto : {ok}/{len(reports)} payload(s) envoyé(s)")
        else:
            report["ok"] = True  # rien à envoyer : semaine vide, pas une erreur
            report["notes"].append("semaine sans données — rien à exporter")
    else:
        report["ok"] = True  # mode queue : l'export en file suffit
        report["notes"].append("mode queue : payload en file (aucun envoi réseau)")

    return report


class Dhis2Scheduler:
    """Boucle asyncio : déclenche run_weekly_job à chaque créneau dû."""

    def __init__(self, tick_s: float = _TICK_S) -> None:
        self._tick_s = tick_s
        self._task: asyncio.Task | None = None
        self._lock = threading.Lock()

    # -- cycle -------------------------------------------------------------
    async def _loop(self) -> None:
        while True:
            try:
                cfg = config_from_env()
                state = load_state()
                nxt = next_occurrence(local_now(), cfg["day"], cfg["hour_utc"])
                if state.get("next_run") and state["next_run"] > \
                        local_now().isoformat(timespec="seconds"):
                    nxt = datetime.fromisoformat(state["next_run"])
                if local_now() >= nxt:
                    report = await asyncio.to_thread(run_weekly_job)
                    state.update(report)
                    state["next_run"] = next_occurrence(
                        local_now(), cfg["day"], cfg["hour_utc"]
                    ).isoformat(timespec="seconds")
                    with self._lock:
                        save_state(state)
            except Exception as e:  # noqa: BLE001 — le cron ne doit jamais tuer le service
                try:
                    state = load_state()
                    state["last_error"] = f"{type(e).__name__}: {e}"
                    state["last_error_at"] = local_now().isoformat(timespec="seconds")
                    with self._lock:
                        save_state(state)
                except Exception:  # pragma: no cover
                    pass
            await asyncio.sleep(self._tick_s)

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.get_event_loop().create_task(self._loop())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
            self._task = None


_scheduler: Dhis2Scheduler | None = None


def get_scheduler() -> Dhis2Scheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = Dhis2Scheduler()
    return _scheduler


def status() -> dict:
    """État consolidé pour l'API/UI : config + dernier rapport + prochain créneau."""
    cfg = config_from_env()
    state = load_state()
    nxt = state.get("next_run")
    if not nxt and cfg["auto"] != "off":
        nxt = next_occurrence(local_now(), cfg["day"],
                              cfg["hour_utc"]).isoformat(timespec="seconds")
    return {"config": cfg, "state": state, "next_run": nxt,
            "period_exported": previous_period(local_now())}
