"""Surveillance — cartographie des éclosions (V1.3).

Couverture : résolution région → district CI (accents, préfixes, hors-CI),
clusters par district depuis les analyses persistées, signal d'éclosion
(+2 cas vs semaine précédente), compartiment non-localisés, route API.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from tropirag.integrations.surveillance import (
    CI_DISTRICTS,
    OutbreakMonitor,
    resolve_district,
)
from tropirag.persistence.database import Database


@pytest.fixture()
def db(tmp_path):
    return Database(tmp_path / "surv.sqlite3")


def _save_case(db, case_id, payload, urgency="priority", severity="moderate",
              diseases=("malaria",), created=None):
    db.execute(
        "INSERT OR REPLACE INTO cases (case_id, created_at, patient_json, payload_json) "
        "VALUES (?,?,?,?)",
        (case_id, created or "2026-09-10T10:00:00",
         json.dumps({"age_years": 30}), json.dumps(payload, ensure_ascii=False)))
    db.execute(
        "INSERT INTO analyses (case_id, created_at, urgency, severity, differentials_json,"
        " matched_rules_json, ai_layer, refusal) VALUES (?,?,?,?,?,?,?,?)",
        (case_id, created or "2026-09-10T10:00:00", urgency, severity,
         json.dumps([{"disease": d, "excluded": False} for d in diseases]),
         json.dumps([]), "deterministic", None))


class TestResolveDistrict:
    def test_14_districts_definis(self):
        assert len(CI_DISTRICTS) == 14
        assert all(d.chief_town for d in CI_DISTRICTS.values())

    @pytest.mark.parametrize("region,expected", [
        ("Bouaké", "vallee-du-bandama"),
        ("bouake", "vallee-du-bandama"),
        ("Korhogo", "savanes"),
        ("San-Pédro", "bas-sassandra"),
        ("Man", "montagnes"),
        ("Abidjan", "abidjan"),
        ("District de Daloa", "sassandra-marahoue"),
        ("région de Gagnoa", "goh-djiboua"),
        ("BONDoukou", "zanzan"),
    ])
    def test_resolutions_courantes(self, region, expected):
        assert resolve_district(region) == expected

    def test_hors_correspondance(self):
        assert resolve_district("Dakar") is None
        assert resolve_district("") is None
        assert resolve_district(None) is None


class TestClusters:
    def test_cluster_par_district(self, db):
        _save_case(db, "c1", {"travel": {"segments": [
            {"country": "CI", "region": "Bouaké"}]}},
            diseases=("malaria",))
        _save_case(db, "c2", {"travel": {"segments": [
            {"country": "CI", "region": "Korhogo"}]}},
            urgency="immediate", severity="critical", diseases=("meningococcal",))
        snap = OutbreakMonitor(db).clusters(days=30)
        by_key = {d["key"]: d for d in snap["districts"]}
        assert by_key["vallee-du-bandama"]["cases"] == 1
        kor = by_key["savanes"]
        assert kor["cases"] == 1 and kor["urgent"] == 1 and kor["critical"] == 1
        assert kor["by_disease"]["meningococcal"] == 1
        assert snap["total_cases"] == 2

    def test_non_localises_jamais_perdus(self, db):
        _save_case(db, "c1", {"travel": {"segments": [{"country": "CI"}]}},
                   diseases=("dengue",))
        snap = OutbreakMonitor(db).clusters(days=30)
        assert snap["non_localises"]["cases"] == 1
        assert snap["total_cases"] == 1
        assert snap["non_localises"]["by_disease"]["dengue"] == 1

    def test_signal_eclosion(self, db):
        # 3 cas cette semaine à Bouaké, 1 la semaine passée → signal
        for i in range(3):
            _save_case(db, f"now{i}", {"travel": {"segments": [
                {"country": "CI", "region": "Bouaké"}]}},
                created="2026-09-10T09:00:00", diseases=("malaria",))
        _save_case(db, "prev", {"travel": {"segments": [
            {"country": "CI", "region": "Bouaké"}]}},
            created="2026-09-01T09:00:00", diseases=("malaria",))
        snap = OutbreakMonitor(db).clusters(days=30)
        ob = [o for o in snap["outbreaks"] if o["district"] == "vallee-du-bandama"]
        assert ob, "signal d'éclosion attendu (+2 cas vs semaine précédente)"
        assert ob[0]["cases_last_week"] >= 3

    def test_segments_hors_ci_ignores(self, db):
        _save_case(db, "c1", {"travel": {"segments": [
            {"country": "PK", "region": "Bouaké"}]}},  # région CI mais pays PK
            diseases=("enteric_fever",))
        snap = OutbreakMonitor(db).clusters(days=30)
        assert snap["districts"] == [], "le district n'est résolu que depuis un segment CI"

    def test_meta_districts_exposee(self, db):
        snap = OutbreakMonitor(db).clusters(days=30)
        assert len(snap["districts_meta"]) == 14


class TestRouteAPI:
    @pytest.fixture()
    def client_with_db(self, tmp_path, monkeypatch):
        """Client API sur une base jetable isolée (singleton sauvegardé/restauré)."""
        monkeypatch.setenv("TROPIRAG_API_KEY", "")
        old_instance = Database._instance
        Database._instance = None
        d = Database.instance(tmp_path / "api_map.sqlite3")
        _save_case(d, "c1", {"travel": {"segments": [
            {"country": "CI", "region": "Abidjan"}]}}, diseases=("dengue",))

        from tropirag.api.routes import surveillance as routes

        routes._monitor = None  # re-résolution avec la base jetable
        from tropirag.api.app import create_app

        client = TestClient(create_app())
        yield client
        routes._monitor = None
        d.close()
        Database._instance = old_instance

    def test_route_surveillance_map(self, client_with_db):
        r = client_with_db.get("/api/v1/surveillance/map?days=30")
        assert r.status_code == 200
        data = r.json()
        assert data["total_cases"] == 1
        assert any(d["key"] == "abidjan" and d["cases"] == 1
                   for d in data["districts"])
        assert len(data["districts_meta"]) == 14

    def test_district_inconnu_404(self, client_with_db):
        r = client_with_db.get("/api/v1/surveillance/map?district=paris")
        assert r.status_code == 404

    def test_page_map_publique(self, client_with_db):
        r = client_with_db.get("/map.html")
        assert r.status_code == 200
        assert "éclosions" in r.text.lower()
