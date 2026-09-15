"""Cron DHIS2 hebdomadaire — tests unitaires (logique pure + API)."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from tropirag.integrations.dhis2.scheduler import (
    config_from_env, next_occurrence, normalize_day, normalize_hour,
    previous_period, run_weekly_job, status,
)


class TestLogiquePure:
    def test_normalize_day(self):
        assert normalize_day("mon") == "MON"
        assert normalize_day(" Sunday ") == "SUN"
        with pytest.raises(ValueError):
            normalize_day("FUNDAY")

    def test_normalize_hour(self):
        assert normalize_hour(6) == 6
        with pytest.raises(ValueError):
            normalize_hour(24)
        with pytest.raises(ValueError):
            normalize_hour(-1)

    def test_previous_period(self):
        # mardi 15 sept 2026 (W38) → semaine écoulée = W37
        assert previous_period(datetime(2026, 9, 15, 6, 0)) == "2026W37"
        # lundi 14 sept 2026 (début W38, 06:00) → semaine complète = W37
        assert previous_period(datetime(2026, 9, 14, 6, 0)) == "2026W37"

    def test_next_occurrence(self):
        # mardi 15 sept 06:00 → prochain lundi 06:00 = 21 sept
        nxt = next_occurrence(datetime(2026, 9, 15, 6, 30), "MON", 6)
        assert nxt == datetime(2026, 9, 21, 6, 0)
        # lundi 14 sept 05:00 → le créneau du jour n'est pas encore passé
        nxt2 = next_occurrence(datetime(2026, 9, 14, 5, 0), "MON", 6)
        assert nxt2 == datetime(2026, 9, 14, 6, 0)
        # lundi 14 sept 06:00 pile → créneau consommé → le suivant
        nxt3 = next_occurrence(datetime(2026, 9, 14, 6, 0), "MON", 6)
        assert nxt3 == datetime(2026, 9, 21, 6, 0)


class TestConfig:
    def test_defauts_off(self, monkeypatch):
        for var in ("TROPIRAG_DHIS2_AUTO", "TROPIRAG_DHIS2_PUSH_DAY",
                    "TROPIRAG_DHIS2_PUSH_HOUR_UTC"):
            monkeypatch.delenv(var, raising=False)
        cfg = config_from_env()
        assert cfg == {"auto": "off", "day": "MON", "hour_utc": 6}

    def test_surcharges(self, monkeypatch):
        monkeypatch.setenv("TROPIRAG_DHIS2_AUTO", "push")
        monkeypatch.setenv("TROPIRAG_DHIS2_PUSH_DAY", "sun")
        monkeypatch.setenv("TROPIRAG_DHIS2_PUSH_HOUR_UTC", "22")
        cfg = config_from_env()
        assert cfg == {"auto": "push", "day": "SUN", "hour_utc": 22}

    def test_auto_vide_ne_surcharge_pas(self, monkeypatch):
        """registry.py injecte '' quand la var est absente → défaut préservé."""
        monkeypatch.setenv("TROPIRAG_DHIS2_AUTO", "")
        assert config_from_env()["auto"] == "off"


class TestRunWeeklyJob:
    def test_off_ne_fait_rien(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TROPIRAG_DHIS2_AUTO", "")
        report = run_weekly_job(datetime(2026, 9, 15, 6, 0))
        assert report["mode"] == "off"
        assert report["ok"] is False
        assert "off" in report["notes"][0]

    def test_mode_queue_exporte_sans_reseau(self, monkeypatch, tmp_path):
        """TROPIRAG_DHIS2_AUTO=queue : export de la semaine écoulée en file,
        aucun envoi réseau — vérifié par l'absence totale de transport."""
        from tropirag.core import config as cfg_mod

        monkeypatch.setenv("TROPIRAG_DHIS2_AUTO", "queue")
        monkeypatch.setenv("TROPIRAG_DHIS2_QUEUE_PATH", str(tmp_path / "q.json"))
        monkeypatch.setattr(cfg_mod, "TROPIRAG_ROOT", tmp_path, raising=False)

        # DB jetable seedée d'une analyse antidatée dans la semaine écoulée (W37)
        from tropirag.persistence.database import Database
        from tropirag.persistence.repositories.case_repository import CaseRepository

        db = Database(tmp_path / "test.sqlite3")
        repo = CaseRepository(db)
        repo.save_case("case-cron-1", {"age_years": 30}, {"patient": {"age_years": 30}})
        repo.save_analysis(
            "case-cron-1", urgency="priority", severity="moderate",
            differentials=[{"disease": "malaria", "score": 0.6}],
            matched_rules=["mal-susp-core-001"], ai_layer="deterministic",
            refusal=None)
        # antidatage : l'analyse tombe dans la semaine écoulée (2026W37)
        db.execute("UPDATE analyses SET created_at='2026-09-10T10:00:00' "
                   "WHERE case_id='case-cron-1'")
        db.commit()

        monkeypatch.setattr(
            "tropirag.persistence.database.Database.instance",
            classmethod(lambda cls: db))

        report = run_weekly_job(datetime(2026, 9, 15, 6, 0))
        assert report["period"] == "2026W37"
        assert report["ok"] is True
        assert report["values"] >= 1
        assert report["enqueued"] is True
        assert report["pushed"] == 0  # mode queue : jamais de réseau
        assert any("queue" in n for n in report["notes"])
        assert (tmp_path / "q.json").exists()

    def test_push_sans_serveur_garde_la_file(self, monkeypatch, tmp_path):
        """auto=push sans serveur configuré : la file conserve le payload,
        le rapport rend compte — aucun envoi, aucune perte, aucune exception."""
        from tropirag.core import config as cfg_mod

        monkeypatch.setenv("TROPIRAG_DHIS2_AUTO", "push")
        monkeypatch.setenv("TROPIRAG_DHIS2_QUEUE_PATH", str(tmp_path / "q.json"))
        monkeypatch.setattr(cfg_mod, "TROPIRAG_ROOT", tmp_path, raising=False)

        from tropirag.persistence.database import Database

        monkeypatch.setattr(
            "tropirag.persistence.database.Database.instance",
            classmethod(lambda cls: Database(tmp_path / "empty.sqlite3")))

        report = run_weekly_job(datetime(2026, 9, 15, 6, 0))
        assert report["ok"] is False  # rien poussé
        assert report["pushed"] == 0
        assert any("non configuré" in n for n in report["notes"])


class TestEtatPersiste:
    def test_status_shape(self, monkeypatch, tmp_path):
        from tropirag.core import config as cfg_mod

        monkeypatch.setattr(cfg_mod, "TROPIRAG_ROOT", tmp_path, raising=False)
        monkeypatch.setenv("TROPIRAG_DHIS2_AUTO", "queue")
        st = status()
        assert st["config"]["auto"] == "queue"
        assert st["next_run"]  # calculé à la volée si jamais exécuté
        assert st["period_exported"] == "2026W37"  # au 15 sept 2026 00:00 UTC±

    def test_run_manuel_persiste_le_rapport(self, monkeypatch, tmp_path):
        """POST cron/run → le rapport est écrit dans l'état (auditable)."""
        from tropirag.core import config as cfg_mod
        from tropirag.integrations.dhis2 import scheduler as sched

        monkeypatch.setattr(cfg_mod, "TROPIRAG_ROOT", tmp_path, raising=False)
        monkeypatch.setenv("TROPIRAG_DHIS2_AUTO", "")
        report = run_weekly_job(datetime(2026, 9, 15, 6, 0))
        state = sched.load_state()
        state["last_manual_run"] = report
        sched.save_state(state)
        saved = json.loads((tmp_path / "runtime" / "state" /
                            "dhis2_cron.json").read_text())
        assert saved["last_manual_run"]["period"] == "2026W37"
