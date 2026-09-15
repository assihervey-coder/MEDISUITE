"""Export DHIS2 — tests unitaires V1.2 (mapper, formats, file offline, transport)."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from tropirag.integrations.dhis2.exporter import Dhis2Exporter
from tropirag.integrations.dhis2.mapper import (
    Dhis2Mapper,
    period_bounds,
    period_from_date,
)
from tropirag.integrations.dhis2.models import DataValue, DataValueSet
from tropirag.integrations.dhis2.queue import OfflineQueue
from tropirag.integrations.dhis2.settings import Dhis2Config, DataElementSpec
from tropirag.integrations.dhis2.transport import (
    Dhis2Transport,
    TransportNotConfigured,
)


def _cfg(tmp_path: Path, mode: str = "offline_queue") -> Dhis2Config:
    return Dhis2Config(
        mode=mode, org_unit="OU-CI-TEST",
        data_elements={
            "total_cases": DataElementSpec("DE-0001"),
            "suspect_malaria": DataElementSpec("DE-0101"),
            "suspect_severe_malaria": DataElementSpec("DE-0102"),
            "suspect_dengue": DataElementSpec("DE-0201"),
            "suspect_enteric_fever": DataElementSpec("DE-0301"),
            "typhoid_xdr": DataElementSpec("DE-0302"),
            "malaria_renal_rrt": DataElementSpec("DE-0103"),
            "dengue_peds_critical": DataElementSpec("DE-0203"),
            "urgent_cases": DataElementSpec("DE-0701"),
            "critical_cases": DataElementSpec("DE-0702"),
        },
        queue_path=tmp_path / "queue.json",
    )


def _row(case_id: str, diseases: list[str], rules: list[str],
         urgency: str = "priority", severity: str = "moderate") -> dict:
    return {
        "case_id": case_id,
        "created_at": "2026-09-10T10:00:00",
        "urgency": urgency,
        "severity": severity,
        "differentials_json": json.dumps([{"disease": d, "score": 0.5} for d in diseases]),
        "matched_rules_json": json.dumps(rules),
    }


class TestPeriodes:
    def test_format_iso(self):
        assert period_from_date(date(2026, 9, 12)) == "2026W37"

    def test_bounds_aller_retour(self):
        start, end = period_bounds("2026W37")
        assert period_from_date(start) == "2026W37"
        assert period_from_date(end) == "2026W37"
        assert (end - start).days == 6

    def test_invalide(self):
        assert period_bounds("nimporte") is None


class TestMapper:
    def test_compteurs_par_maladie(self, tmp_path):
        m = Dhis2Mapper(_cfg(tmp_path))
        rows = [
            _row("c1", ["malaria"], ["mal-susp-core-001"], urgency="emergency"),
            _row("c2", ["severe_malaria"], ["mal-renal-aki-001", "mal-renal-rrt-indicated-004"],
                 urgency="immediate", severity="critical"),
            _row("c3", ["dengue"], ["den-susp-core-001"]),
            _row("c4", ["enteric_fever"], ["typ-susp-core-001", "typ-xdr-travel-risk-001"]),
        ]
        c = m.counts(rows)
        assert c["total_cases"] == 4
        assert c["suspect_malaria"] == 2           # malaria + severe_malaria
        assert c["suspect_severe_malaria"] == 1
        assert c["malaria_renal_rrt"] == 1
        assert c["suspect_dengue"] == 1
        assert c["suspect_enteric_fever"] == 1
        assert c["typhoid_xdr"] == 1
        assert c["urgent_cases"] == 2
        assert c["critical_cases"] == 1

    def test_map_produit_des_datavalues(self, tmp_path):
        m = Dhis2Mapper(_cfg(tmp_path))
        dvs = m.map([_row("c1", ["malaria"], ["mal-susp-core-001"])], "2026W37")
        assert dvs.org_unit == "OU-CI-TEST"
        assert dvs.period == "2026W37"
        uids = {dv.data_element for dv in dvs.data_values}
        assert {"DE-0001", "DE-0101"} <= uids
        for dv in dvs.data_values:
            assert dv.period == "2026W37"
            assert dv.org_unit == "OU-CI-TEST"

    def test_zero_valeur_non_exportee(self, tmp_path):
        dvs = Dhis2Mapper(_cfg(tmp_path)).map([], "2026W37")
        assert len(dvs) == 0


class TestFormats:
    def test_json_datavaluesets(self):
        dv = DataValue(data_element="DE-0101", org_unit="OU", period="2026W37", value="7")
        payload = DataValueSet(data_values=[dv]).to_json_payload()
        assert payload["dataValues"][0]["dataElement"] == "DE-0101"
        assert payload["dataValues"][0]["value"] == "7"

    def test_csv_structure(self):
        dv = DataValue(data_element="DE-0101", org_unit="OU", period="2026W37", value="7")
        csv = DataValueSet(data_values=[dv]).to_csv()
        lines = csv.strip().split("\n")
        assert lines[0] == "dataelement,orgunit,period,value,categoryoptioncombo"
        assert lines[1].startswith("DE-0101,OU,2026W37,7")

    def test_adx_xml(self):
        dv = DataValue(data_element="DE-0101", org_unit="OU", period="2026W37", value="7")
        adx = DataValueSet(data_values=[dv], org_unit="OU", period="2026W37").to_adx()
        assert 'xmlns:adx="urn:ihe:iti:adx:2015"' in adx
        assert '<adx:group orgUnit="OU" period="2026W37">' in adx
        assert 'dataElement="DE-0101" value="7"' in adx

    def test_rendus_via_exporter(self, tmp_path):
        exp = Dhis2Exporter(_cfg(tmp_path))
        dvs = DataValueSet(
            data_values=[DataValue(data_element="DE-0101", org_unit="OU",
                                    period="2026W37", value="3")],
            org_unit="OU", period="2026W37")
        for fmt in ("json", "csv", "adx"):
            out = exp.render(dvs, fmt)
            assert isinstance(out, str) and "DE-0101" in out
        with pytest.raises(ValueError):
            exp.render(dvs, "xml-unknown")


class TestFileOffline:
    def test_enqueue_persist_et_recharge(self, tmp_path):
        q = OfflineQueue(tmp_path / "q.json")
        entry = q.enqueue({"dataValues": []}, meta={"period": "2026W37"})
        assert entry["status"] == "pending"

        # rechargement depuis le disque — le district peut redémarrer
        q2 = OfflineQueue(tmp_path / "q.json")
        assert len(q2.pending()) == 1
        assert q2.pending()[0]["id"] == entry["id"]

    def test_mark_sent(self, tmp_path):
        q = OfflineQueue(tmp_path / "q.json")
        entry = q.enqueue({"x": 1})
        q.mark(entry["id"], "sent", note="201")
        assert q.pending() == []
        assert q.status_summary()["by_status"].get("sent") == 1

    def test_fichier_corrompu_repart_propre(self, tmp_path):
        p = tmp_path / "q.json"
        p.write_text("{{{{not json", encoding="utf-8")
        q = OfflineQueue(p)
        assert q.status_summary()["total"] == 0


class TestTransport:
    def test_non_configure_leve(self, tmp_path):
        t = Dhis2Transport(_cfg(tmp_path))
        with pytest.raises(TransportNotConfigured):
            t.push({"dataValues": []})

    def test_push_ok_avec_serveur_mock(self, tmp_path):
        cfg = _cfg(tmp_path, mode="push")
        cfg.base_url = "https://dhis2.example/api"
        cfg.username = "user"

        class _Resp:
            status_code = 200
            text = "imported"

        t = Dhis2Transport(cfg, http_post=lambda url, **kw: _Resp())
        report = t.push({"dataValues": []})
        assert report.ok and report.status_code == 200

    def test_push_echec_reseau(self, tmp_path):
        cfg = _cfg(tmp_path, mode="push")
        cfg.base_url = "https://dhis2.example/api"
        cfg.username = "user"

        def _boom(url, **kw):
            raise ConnectionError("pas de réseau")

        report = Dhis2Transport(cfg, http_post=_boom).push({"dataValues": []})
        assert not report.ok
        assert "réseau" in report.detail


class TestExporteur:
    def test_dry_run_ne_prend_pas_la_file(self, tmp_path):
        exp = Dhis2Exporter(_cfg(tmp_path))
        rows = [_row("c1", ["malaria"], ["mal-susp-core-001"])]
        result = exp.export(rows, "2026W37", enqueue=False)
        assert not result.enqueued
        assert exp.queue.status_summary()["total"] == 0
        assert result.counts["suspect_malaria"] == 1

    def test_enqueue_par_defaut_mode_offline(self, tmp_path):
        exp = Dhis2Exporter(_cfg(tmp_path))  # mode offline_queue par défaut
        rows = [_row("c1", ["malaria"], ["mal-susp-core-001"])]
        result = exp.export(rows, "2026W37")  # None → suit la config
        assert result.enqueued
        assert exp.queue.pending()


class TestConfiguration:
    """Surcharges environnementales — branchement serveur réel MSP-CI."""

    def test_surcharges_env_completes(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TROPIRAG_DHIS2_MODE", "push")
        monkeypatch.setenv("TROPIRAG_DHIS2_BASE_URL", "https://dhis2.msp-ci.gouv.ci/api")
        monkeypatch.setenv("TROPIRAG_DHIS2_USERNAME", "tropirag-export")
        monkeypatch.setenv("TROPIRAG_DHIS2_ORG_UNIT", "OU-CI-ABJ-01")
        monkeypatch.setenv("TROPIRAG_DHIS2_QUEUE_PATH", str(tmp_path / "q.json"))
        cfg = Dhis2Config.from_yaml(tmp_path / "absent.yaml")  # défauts + env
        assert cfg.mode == "push"
        assert cfg.base_url == "https://dhis2.msp-ci.gouv.ci/api"
        assert cfg.username == "tropirag-export"
        assert cfg.org_unit == "OU-CI-ABJ-01"
        assert str(cfg.queue_path) == str(tmp_path / "q.json")
        assert cfg.transport_ready  # base_url + username → push possible

    def test_env_vide_ne_surcharge_pas(self, monkeypatch):
        monkeypatch.setenv("TROPIRAG_DHIS2_MODE", "")
        monkeypatch.setenv("TROPIRAG_DHIS2_BASE_URL", "")
        cfg = Dhis2Config.from_yaml()
        assert cfg.mode == "offline_queue"  # défaut YAML préservé
        assert cfg.base_url is None
        assert not cfg.transport_ready

    def test_mdp_jamais_en_clair_dans_la_config(self, monkeypatch):
        """Le mot de passe ne vit QUE dans la variable d'env dédiée."""
        monkeypatch.setenv("TROPIRAG_DHIS2_PASSWORD", "s3cr3t-msp")
        cfg = Dhis2Config.from_yaml()
        assert "s3cr3t" not in repr(cfg)
        import os

        assert os.environ["TROPIRAG_DHIS2_PASSWORD"] == "s3cr3t-msp"


class TestAPIRoutes:
    """Routes /api/v1/export/dhis2 — intégration avec DB jetable."""

    @pytest.fixture()
    def client(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TROPIRAG_API_KEY", "")
        import importlib

        import tropirag.core.config as cfg
        importlib.reload(cfg)
        from tropirag.api import app as app_mod
        importlib.reload(app_mod)
        return app_mod

    def test_export_dry_run_via_api(self, client, monkeypatch, tmp_path):
        import tropirag.api.routes.export as export_mod

        db = _fresh_db(tmp_path)
        _seed_analysis(db)
        monkeypatch.setattr(export_mod, "_db", db)
        monkeypatch.setattr(export_mod, "_exporter", Dhis2Exporter(_cfg(tmp_path)))

        from fastapi.testclient import TestClient

        r = TestClient(client.app).post("/api/v1/export/dhis2", json={
            "period": period_from_date(date.today()), "format": "json",
            "enqueue": False,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["counts"]["total_cases"] == 1
        assert data["counts"]["suspect_malaria"] == 1
        assert not data["enqueued"]
        assert data["data_values"]
        payload = data["payload"]
        assert "dataValues" in payload  # rendu JSON DHIS2

    def test_status_via_api(self, client, monkeypatch, tmp_path):
        import tropirag.api.routes.export as export_mod

        monkeypatch.setattr(export_mod, "_db", _fresh_db(tmp_path))
        monkeypatch.setattr(export_mod, "_exporter", Dhis2Exporter(_cfg(tmp_path)))

        from fastapi.testclient import TestClient

        r = TestClient(client.app).get("/api/v1/export/dhis2/status")
        assert r.status_code == 200
        body = r.json()
        assert body["queue"]["path"].endswith("queue.json")
        assert body["config"]["mode"] == "offline_queue"
        assert body["config"]["elements_mapped"] >= 10

    def test_pousse_sans_configuration_echoue_proprement(self, client, monkeypatch, tmp_path):
        import tropirag.api.routes.export as export_mod

        monkeypatch.setattr(export_mod, "_db", _fresh_db(tmp_path))
        monkeypatch.setattr(export_mod, "_exporter", Dhis2Exporter(_cfg(tmp_path)))

        from fastapi.testclient import TestClient

        r = TestClient(client.app).post("/api/v1/export/dhis2/push")
        assert r.status_code == 200
        assert r.json()["detail"] == "aucun payload en attente"


def _fresh_db(tmp_path: Path):
    from tropirag.persistence.database import Database

    return Database(tmp_path / "test.sqlite3")


def _seed_analysis(db) -> None:
    from tropirag.persistence.repositories.case_repository import CaseRepository

    repo = CaseRepository(db)
    repo.save_case("case-dhis2-1", {"age_years": 30}, {"patient": {"age_years": 30}})
    repo.save_analysis(
        "case-dhis2-1", urgency="emergency", severity="severe",
        differentials=[{"disease": "malaria", "score": 0.7}],
        matched_rules=["mal-susp-core-001", "mal-sev-cerebral-001"],
        ai_layer="deterministic", refusal=None)
