"""Tests ecrf-service (v0.7) : sujets, saisie, signature, amendement,
monitoring SDV, sync offline idempotente, export DSMB, audit chaîné, HAPI."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core",
          str(ROOT / "services" / "ecrf-service" / "src")):
    sys.path.insert(0, p)

# BDD fraîche par run (principe v0.1 « idempotence ») : le verrou de base
# M+18 est IRRÉVERSIBLE par conception (EGSP) — une base de dev persistante
# condamnerait toute ré-exécution locale de la suite (409 partout après le
# premier run ayant posé le lock). On repart donc d'une base vide AVANT
# l'import de main (le moteur est créé à l'import). En CI le fichier
# n'existe pas : comportement identique.
for _suffix in ("", "-wal", "-shm"):
    _db = ROOT / "data" / f"ecrf-service.db{_suffix}"
    if _db.exists():
        _db.unlink()

from fastapi.testclient import TestClient
from main import app, JWT_SECRET, HAPI, FHIR_PUSH_ENABLED
from medisuite_core import security

client = TestClient(app)


def _tok(sub: str, role: str) -> dict:
    return {"Authorization": f"Bearer "
            f"{security.jwt_encode({'sub': sub, 'role': role}, JWT_SECRET)}"}


MED = _tok("dr-yao", "medecin")            # investigateur de terrain
ADJ = _tok("pr-kone", "adjudicateur")      # comité aveugle
MON = _tok("monitor-ext", "moniteur")      # moniteur indépendant
PRM = _tok("sponsor", "promoteur")
DM = _tok("dm-site", "data_manager")

SUBJ = {"site": "COC", "scenario": "S1", "consentement": "ecrit",
        "age": 54, "date_passage": "2026-10-01", "perte_modalites": 0}

F03 = {"decision_standard": "TDM + surveillance", "decision_finale": "rtPA",
       "adhesion": "acceptee", "dispositif_consulte": True,
       "horodatage_triage": "2026-10-01T08:00",
       "horodatage_orientation": "2026-10-01T08:39"}

F05 = {"verdict_standard": "AVC ischémique", "verdict_final": "AVC ischémique",
       "certitude": 4, "tierce_requis": False, "dossier_complet": True}


def _subject() -> str:
    r = client.post("/api/v1/ecrf/subjects", json=SUBJ, headers=MED)
    assert r.status_code == 201, r.text
    return r.json()["code"]


# ── Catalogue et RBAC ────────────────────────────────────────────────────────

def test_forms_necessite_auth():
    assert client.get("/api/v1/ecrf/forms").status_code == 403


def test_forms_catalogue():
    r = client.get("/api/v1/ecrf/forms", headers=MED)
    assert r.status_code == 200
    body = r.json()
    assert body["study"] == "MEDISUITE-CI-01"
    assert {f["id"] for f in body["forms"]} == {
        "F01-INCLUSION", "F02-BASELINE", "F03-DECISION", "F04-SUIVI30J",
        "F05-ADJUDICATION", "F06-DEVIATION"}
    assert len(body["sites"]) == 4 and len(body["scenarios"]) == 5


def test_inclusion_sujet_201_et_sequentiel():
    c1 = _subject()
    c2 = _subject()
    assert c1 == "CI01-COC-00001" and c2 == "CI01-COC-00002"
    assert client.post("/api/v1/ecrf/subjects", json=SUBJ, headers=MON)\
        .status_code == 403  # moniteur : lecture/monitoring seulement


def test_inclusion_erreurs():
    assert client.post("/api/v1/ecrf/subjects",
                       json=SUBJ | {"site": "XXX"}, headers=MED)\
        .status_code == 422
    assert client.post("/api/v1/ecrf/subjects",
                       json=SUBJ | {"consentement": "refuse"}, headers=MED)\
        .status_code == 422
    assert client.post("/api/v1/ecrf/subjects",
                       json=SUBJ | {"age": 15}, headers=MED).status_code == 422


def test_inclusion_grossesse_s2_non_eligible():
    r = client.post("/api/v1/ecrf/subjects",
                    json=SUBJ | {"scenario": "S2", "grossesse": True},
                    headers=MED).json()
    assert r["statut"] == "non_eligible" and "grossesse" in r["motif"]


# ── Saisie, idempotence, séparation des rôles ───────────────────────────────

def test_saisie_f03_et_rejeu_idempotent():
    code = _subject()
    r1 = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                     json=F03, headers=MED)
    assert r1.status_code == 200 and r1.json()["duplicate"] is False
    r2 = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                     json=F03, headers=MED)  # rejeu offline → pas de doublon
    assert r2.json()["duplicate"] is True
    assert r2.json()["entry_id"] == r1.json()["entry_id"]


def test_saisie_validation_422():
    code = _subject()
    bad = F03 | {"adhesion": "peut-etre"}
    r = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                    json=bad, headers=MED)
    assert r.status_code == 422
    assert any("adhesion" in str(e) for e in r.json()["detail"]["details"])


def test_separation_adjudication_aveugle():
    code = _subject()
    # investigateur : JAMAIS le F05 (aveuglement §3.3)
    assert client.post(
        f"/api/v1/ecrf/subjects/{code}/forms/F05-ADJUDICATION",
        json=F05, headers=MED).status_code == 403
    # comité : uniquement le F05
    assert client.post(
        f"/api/v1/ecrf/subjects/{code}/forms/F05-ADJUDICATION",
        json=F05, headers=ADJ).status_code == 200
    assert client.post(
        f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
        json=F03, headers=ADJ).status_code == 403


def test_sujet_inconnu_404():
    r = client.post("/api/v1/ecrf/subjects/CI01-COC-99999/forms/F03-DECISION",
                    json=F03, headers=MED)
    assert r.status_code == 404


# ── Signature et amendement ──────────────────────────────────────────────────

def test_signature_verrouille():
    code = _subject()
    entry = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                        json=F03, headers=MED).json()["entry_id"]
    assert client.post(f"/api/v1/ecrf/entries/{entry}/sign",
                       headers=MON).status_code == 403  # pas de ecrf.sign
    r = client.post(f"/api/v1/ecrf/entries/{entry}/sign", headers=MED)
    assert r.status_code == 200 and r.json()["statut"] == "signe"
    assert client.post(f"/api/v1/ecrf/entries/{entry}/sign",
                       headers=MED).status_code == 409  # re-signature


def test_amendement_versionne_original_intact():
    code = _subject()
    entry = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                        json=F03, headers=MED).json()["entry_id"]
    # amendement AVANT signature → refusé
    assert client.post(f"/api/v1/ecrf/entries/{entry}/amend",
                       json={"motif": "correction horodatage",
                             "payload": F03}, headers=MED).status_code == 409
    client.post(f"/api/v1/ecrf/entries/{entry}/sign", headers=MED)
    f03_corrige = F03 | {"horodatage_orientation": "2026-10-01T08:41"}
    r = client.post(f"/api/v1/ecrf/entries/{entry}/amend",
                    json={"motif": "correction horodatage orientation",
                          "payload": f03_corrige}, headers=MED)
    assert r.status_code == 200 and r.json()["version"] == 2
    # l'original reste intact et signé
    detail = client.get(f"/api/v1/ecrf/subjects/{code}", headers=DM).json()
    versions = {e["version"]: (e["id"], e["statut"]) for e in detail["entries"]}
    assert versions[1][0] == entry and versions[1][1] == "signe"
    assert versions[2][1] == "brouillon"


# ── Monitoring SDV ───────────────────────────────────────────────────────────

def test_requete_monitoring_cycle():
    code = _subject()
    assert client.post("/api/v1/ecrf/queries",
                       json={"subject_code": code, "message": "copie F01?"},
                       headers=MED).status_code == 403  # ouvert par moniteur
    qid = client.post("/api/v1/ecrf/queries",
                      json={"subject_code": code,
                            "message": "consentement à vérifier (SDV)"},
                      headers=MON).json()["id"]
    assert client.post(f"/api/v1/ecrf/queries/{qid}/close",
                       json={"reponse": "ok"}, headers=MON).status_code == 403
    assert client.post(f"/api/v1/ecrf/queries/{qid}/close",
                       json={"reponse": "copie archivée site"},
                       headers=MED).status_code == 200
    assert client.post(f"/api/v1/ecrf/queries/{qid}/close",
                       json={"reponse": "encore"}, headers=MED)\
        .status_code == 409
    ouvertes = client.get("/api/v1/ecrf/queries?statut=ouverte",
                          headers=MON).json()
    assert all(q["id"] != qid for q in ouvertes["queries"])


# ── Synchronisation offline ──────────────────────────────────────────────────

def test_sync_lot_mixte_et_rejeu():
    code = _subject()
    items = [
        {"client_key": "k1", "subject_code": code, "form_id": "F03-DECISION",
         "payload": F03},
        {"client_key": "k2", "subject_code": code,
         "form_id": "F02-BASELINE",
         "payload": {"sexe": "M", "tranche_age": "40-59",
                     "provenance": "urgences"}},
        {"client_key": "k3", "subject_code": code, "form_id": "F03-DECISION",
         "payload": F03 | {"adhesion": "peut-etre"}},  # validation KO (hors liste)
        {"client_key": "", "subject_code": code, "form_id": "F02-BASELINE",
         "payload": {"sexe": "F", "tranche_age": "60-74",
                     "provenance": "imagerie"}},   # clé client absente
    ]
    r = client.post("/api/v1/ecrf/sync", json={"items": items}, headers=MED)
    assert r.status_code == 200
    body = r.json()
    assert body["processed"] == 4 and body["created"] == 2
    by_key = {res["client_key"]: res for res in body["results"]}
    assert by_key["k1"]["status"] == "created"
    assert by_key["k2"]["status"] == "created"
    assert by_key["k3"]["status"] == "error"
    assert by_key[""]["status"] == "error"
    # rejeu intégral : k1/k2 deviennent des doublons, rien ne se crée
    r2 = client.post("/api/v1/ecrf/sync", json={"items": items}, headers=MED)
    assert r2.json()["created"] == 0 and r2.json()["duplicate"] == 2


def test_sync_requiert_ecrf_write():
    assert client.post("/api/v1/ecrf/sync", json={"items": [1]},
                       headers=MON).status_code == 403
    assert client.post("/api/v1/ecrf/sync", json={"items": []},
                       headers=MED).status_code == 422


# ── Export DSMB ──────────────────────────────────────────────────────────────

def test_export_dsmb_agreges_sans_phi():
    code = _subject()
    client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                json=F03, headers=MED)
    client.post(f"/api/v1/ecrf/subjects/{code}/forms/F04-SUIVI30J",
                json={"statut_30j": "vivant", "ei_lie_dispositif": True,
                      "ei_gravite": "SAE",
                      "ei_description": "convulsion post-rtPA"},
                headers=MED)
    assert client.get("/api/v1/ecrf/exports/dsmb", headers=MED)\
        .status_code == 403
    out = client.get("/api/v1/ecrf/exports/dsmb", headers=PRM).json()
    assert out["study"] == "MEDISUITE-CI-01"
    assert out["sujets"]["total"] >= 1 and "COC" in out["sujets"]["par_site"]
    assert out["surete"]["SAE_lies_dispositif"] >= 1
    assert out["p3_delai_orientation_min"]["mediane"] == 39.0
    assert out["adhesion"].get("acceptee", 0) >= 1
    # aucune donnée libre ne sort (pas de texte décision/EI)
    assert "decision_standard" not in str(out)


# ── Audit chaîné ─────────────────────────────────────────────────────────────

def test_audit_chaine_integre():
    code = _subject()
    client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                json=F03, headers=MED)
    out = client.get("/api/v1/ecrf/audit/verify", headers=DM).json()
    assert out["integre"] is True and out["premiere_alteration"] is None
    assert out["evenements"] >= 2
    actions = {e["action"] for e in out["tail"]}
    assert "ecrf.submit" in actions


# ── Poussée FHIR optionnelle (HAPI) ─────────────────────────────────────────

class _FakeHapi:
    def __init__(self, mode: str):
        self.mode = mode
        self.bundles: list[dict] = []

    def transaction(self, bundle: dict) -> dict:
        if self.mode == "erreur":
            raise __import__("medisuite_core.hapi_client",
                             fromlist=["FhirError"]).FhirError("500 HAPI")
        if self.mode == "down":
            raise ConnectionError("hub injoignable")
        self.bundles.append(bundle)
        return {"resourceType": "Bundle", "type": "transaction-response"}


def test_fhir_push_puis_hors_ligne(monkeypatch):
    import main
    code = _subject()
    monkeypatch.setattr(main, "FHIR_PUSH_ENABLED", True)
    fake = _FakeHapi("ok")
    monkeypatch.setattr(main, "HAPI", fake)
    r = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F02-BASELINE",
                    json={"sexe": "M", "tranche_age": "40-59",
                          "provenance": "urgences"}, headers=MED)
    assert r.json()["fhir_status"] == "pousse"
    assert len(fake.bundles) == 1
    bundle = fake.bundles[0]
    assert bundle["resourceType"] == "Bundle"
    # le patient pseudonyme porte le code étude, jamais de nom
    patient = bundle["entry"][0]["resource"]
    assert patient["identifier"][0]["value"] == code
    monkeypatch.setattr(main, "HAPI", _FakeHapi("down"))
    r2 = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F06-DEVIATION",
                     json={"type": "panne", "description": "coupure site 3 h",
                           "impact_evaluabilite": False}, headers=MED)
    assert r2.json()["fhir_status"] == "hors_ligne"  # saisie préservée
    monkeypatch.setattr(main, "HAPI", _FakeHapi("erreur"))
    r3 = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F06-DEVIATION",
                     json={"type": "retard_saisie", "description": "retard 2 j",
                           "impact_evaluabilite": False}, headers=MED)
    assert r3.json()["fhir_status"] == "erreur_hapi"


def test_fhir_push_desactive_par_defaut():
    code = _subject()
    r = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F02-BASELINE",
                    json={"sexe": "F", "tranche_age": "18-39",
                          "provenance": "laboratoire"}, headers=MED)
    assert r.json()["fhir_status"] == "desactive"

# ── Verrou de base M+18 et extraction data manager (v0.8, §7.4 protocole) ────
# Séquence ordonnée : UNE SEULE base, UNE SEULE opération de lock (irréversible)
# — les sujets A et B sont préparés AVANT le lock, puis les cas verrouillés
# s'enchaînent. run_tests.py fournit une BDD fraîche par exécution.

STUDY_LOCK = {"temoins": ["temoin-A", "temoin-B"],
              "declaration": "SDV complète, zéro requête ouverte"}
_CODE_A = _CODE_B = None


def _prepare_two_subjects() -> tuple[str, str]:
    """Deux sujets avec F03 signé (créés AVANT tout lock)."""
    codes = []
    for _ in range(2):
        code = _subject()
        _sign_f03(code)
        codes.append(code)
    return codes[0], codes[1]


def _sign_f03(code: str) -> None:
    r = client.post(f"/api/v1/ecrf/subjects/{code}/forms/F03-DECISION",
                    json=F03, headers=MED)
    assert r.status_code == 200, r.text
    eid = r.json()["entry_id"]
    r = client.post(f"/api/v1/ecrf/entries/{eid}/sign", headers=MED)
    assert r.status_code == 200


def test_lock_00_extract_bloquee_avant_verrou():
    global _CODE_A, _CODE_B
    _CODE_A, _CODE_B = _prepare_two_subjects()
    # extraction data manager refusée avant le lock
    r = client.get("/api/v1/ecrf/extract", headers=DM)
    assert r.status_code == 409 and "lock M+18" in r.json()["detail"]
    # statut : base ouverte, checksum indicatif présent
    s = client.get("/api/v1/ecrf/study/status", headers=DM).json()
    assert s["locked"] is False and len(s["checksum_courant"]) == 64
    assert s["requetes_ouvertes"] == 0


def test_lock_01_controles_acces_et_preconditions():
    # 1 témoin → 422 (protocole §8 : verrou + témoins)
    r = client.post("/api/v1/ecrf/study/lock",
                    json={"temoins": ["seul"]}, headers=PRM)
    assert r.status_code == 422
    # investigateur → 403 (ecrf.lock réservé au promoteur)
    assert client.post("/api/v1/ecrf/study/lock",
                       json={"temoins": ["a", "b"]}, headers=MED).status_code == 403
    # data manager → 403 (il EXTRAIT, il ne verrouille pas — séparation GCP)
    assert client.post("/api/v1/ecrf/study/lock",
                       json={"temoins": ["a", "b"]}, headers=DM).status_code == 403
    # requête SDV ouverte → lock refusé (plan-monitoring §5)
    q = client.post("/api/v1/ecrf/queries",
                    json={"subject_code": _CODE_A,
                          "message": "horodatage P3 à justifier vs source"},
                    headers=MON)
    assert q.status_code == 201
    r = client.post("/api/v1/ecrf/study/lock", json=STUDY_LOCK, headers=PRM)
    assert r.status_code == 409 and "requête" in r.json()["detail"]
    # clôture par le site puis LOCK OK
    assert client.post(f"/api/v1/ecrf/queries/{q.json()['id']}/close",
                       json={"reponse": "justifié vs registre arrivée"},
                       headers=MED).status_code == 200
    r = client.post("/api/v1/ecrf/study/lock", json=STUDY_LOCK, headers=PRM)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["locked"] is True and len(body["checksum"]) == 64
    assert body["temoins"] == ["temoin-A", "temoin-B"]
    assert body["extraction"].startswith("débloquée")


def test_lock_02_irreversible_et_toutes_ecritures_gelees():
    # re-lock → 409
    assert client.post("/api/v1/ecrf/study/lock", json=STUDY_LOCK,
                       headers=PRM).status_code == 409
    # inclusion → 409
    assert client.post("/api/v1/ecrf/subjects", json=SUBJ,
                       headers=MED).status_code == 409
    # saisie → 409
    r = client.post(f"/api/v1/ecrf/subjects/{_CODE_A}/forms/F02-BASELINE",
                    json={"sexe": "M", "tranche_age": "40-59",
                          "provenance": "urgences"}, headers=MED)
    assert r.status_code == 409 and "verrouillée" in r.json()["detail"]
    # amendement → 409
    entries = client.get(f"/api/v1/ecrf/subjects/{_CODE_A}",
                         headers=MED).json()["entries"]
    eid = next(e["id"] for e in entries if e["form_id"] == "F03-DECISION")
    r = client.post(f"/api/v1/ecrf/entries/{eid}/amend",
                    json={"motif": "correction post-lock interdite",
                          "payload": F03}, headers=MED)
    assert r.status_code == 409
    # sync offline → items « rejected » (jamais silencieusement perdus)
    r = client.post("/api/v1/ecrf/sync",
                    json={"items": [{"client_key": "k1",
                                     "subject_code": _CODE_A,
                                     "form_id": "F02-BASELINE",
                                     "payload": {"sexe": "M",
                                                 "tranche_age": "40-59",
                                                 "provenance": "urgences"}}]},
                    headers=MED)
    assert r.status_code == 200
    assert r.json()["results"][0]["status"] == "rejected"
    # statut : verrou visible + témoins
    s = client.get("/api/v1/ecrf/study/status", headers=MED).json()
    assert s["locked"] is True and s["temoins"] == ["temoin-A", "temoin-B"]


def test_lock_03_extract_saf_apres_verrou_et_separation_roles():
    # promoteur : verrouille mais n'extrait PAS (ecrf.extract absent)
    assert client.get("/api/v1/ecrf/extract", headers=PRM).status_code == 403
    # investigateur → 403
    assert client.get("/api/v1/ecrf/extract", headers=MED).status_code == 403
    # data manager → SAF complet
    r = client.get("/api/v1/ecrf/extract", headers=DM)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["study"] == "MEDISUITE-CI-01"
    assert body["integrity"]["conforme"] is True
    assert body["integrity"]["checksum_recalcule"] == body["lock"]["checksum"]
    assert body["lock"]["temoins"] == ["temoin-A", "temoin-B"]
    assert body["queries_resolues"] >= 1
    row = next(d for d in body["dataset"] if d["code"] == _CODE_A)
    f03 = row["forms"]["F03-DECISION"]
    assert f03["derivees"]["delai_orientation_min"] == 39.0  # 08:00 → 08:39
    assert f03["signed_by"] == "dr-yao"
    assert "F01-INCLUSION" not in row["forms"]  # non signée → hors SAF
    # extraction tracée dans l'audit chaîné, chaîne intacte
    tail = client.get("/api/v1/ecrf/audit/verify", headers=DM).json()
    assert any(ev["action"] == "ecrf.extract" for ev in tail["tail"])
    assert tail["integre"] is True


def test_lock_04_alarme_integrite_si_donnees_derivent():
    """Altération post-lock (hors API) → extraction 500 + événement audit."""
    import main
    from sqlalchemy import select
    with main.SessionLocal() as session:
        entry = session.scalars(
            select(main.EcrfEntry)
            .where(main.EcrfEntry.subject_code == _CODE_A)
            .where(main.EcrfEntry.form_id == "F03-DECISION")).first()
        mutated = dict(entry.payload)
        mutated["decision_finale"] = "TDM seul"
        entry.payload = mutated
        session.commit()
    r = client.get("/api/v1/ecrf/extract", headers=DM)
    assert r.status_code == 500 and "intégrité" in r.json()["detail"]
    tail = client.get("/api/v1/ecrf/audit/verify", headers=DM).json()
    assert any(ev["action"] == "ecrf.extract.integrity" for ev in tail["tail"])
    assert tail["integre"] is True  # l'ALERTE est elle-même tracée, chaîne OK
