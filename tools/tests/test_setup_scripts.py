"""Tests du setup local 00-10 + paquet hors-ligne (chantier v0.13 —
COUVERTURE-ARBRE-INITIAL §2 bloc `local-deployment/`).

Propriétés verrouillées :
1. SÉQUENCE — scripts 00..10 présents, exécutables, nommage homogène ;
2. DURETÉ — `set -euo pipefail` partout (direct ou via _lib.sh) ;
3. SYNTAXE — `bash -n` passe pour chaque script (setup + offline) ;
4. SÉCURITÉ — ni .env ni certificats générés ne sont versionnés ;
5. RÉFÉRENCES — chaque chemin cité par la compose minimale existe ;
6. BUNDLE — DRY_RUN=1 affiche le plan, exit 0, ne crée RIEN ;
7. INTÉGRITÉ — install-bundle exige MANIFEST.sha256 avant installation ;
8. DOC — READMEs et Makefile raccordés aux scripts réels.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETUP = ROOT / "local-deployment" / "setup"
OFFLINE = ROOT / "local-deployment" / "offline"
COMPOSE = ROOT / "local-deployment" / "docker-compose.minimal.yml"


def _sh_scripts() -> list[Path]:
    return sorted(SETUP.glob("*.sh")) + sorted(OFFLINE.glob("*.sh"))


def test_01_sequence_00_a_10_complete_et_executable():
    attendus = {
        "00-prereqs.sh", "01-python.sh", "02-portal.sh", "03-env.sh",
        "04-certs.sh", "05-secrets.sh", "06-db.sh", "07-images.sh",
        "08-up.sh", "09-smoke.sh", "10-verify.sh",
    }
    presents = {p.name for p in SETUP.glob("[0-9][0-9]-*.sh")}
    assert presents == attendus, f"séquence incomplète : {sorted(attendus ^ presents)}"
    for p in SETUP.glob("[0-9][0-9]-*.sh"):
        assert p.stat().st_mode & 0o111, f"non exécutable : {p.name}"


def test_02_durete_set_eu_pipefail_partout():
    lib = (SETUP / "_lib.sh").read_text(encoding="utf-8")
    assert "set -euo pipefail" in lib, "_lib.sh doit imposer set -euo pipefail"
    for p in _sh_scripts():
        if p.name == "_lib.sh":
            continue
        t = p.read_text(encoding="utf-8")
        assert ("set -euo pipefail" in t) or ("_lib.sh" in t), (
            f"{p.name} : ni set -euo pipefail direct, ni sourcing _lib.sh")


def test_03_syntaxe_bash_valide():
    for p in _sh_scripts():
        r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"syntaxe invalide ({p.name}) : {r.stderr}"


def test_04_secrets_et_certificats_non_versionnes():
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    for f in tracked:
        assert f != "local-deployment/.env", "le .env local est versionné !"
        assert not f.startswith("local-deployment/certs/"), "certificat versionné !"
    # le token dev Vault dans 05-secrets.sh n'est qu'un FALLBACK aligné sur la
    # compose minimale (déjà public) — aucune autre valeur secrète en clair :
    env_example_keys = set(re.findall(r"^([A-Z_]+)=", (SETUP / "03-env.sh").read_text(), re.M))
    assert {"MEDISUITE_JWT_SECRET", "MEDISUITE_ORTHANC_PASSWORD"} <= env_example_keys


def test_05_chemins_cites_par_la_compose_existent():
    base = COMPOSE.parent
    cites = [
        base / "orthanc/orthanc.json",
        base / "hapi/application.yaml",
        base / "ohif/Dockerfile",
        base / "ohif/nginx.conf",
        base / "ohif/app-config.js",
        base / "Dockerfile.service",
        ROOT / "monitoring/otel/collector.yaml",
        ROOT / "monitoring/prometheus/prometheus.yml",
    ]
    for c in cites:
        assert c.exists(), f"référence compose manquante : {c.relative_to(ROOT)}"


def test_06_bundle_dry_run_plan_sans_effet(tmp_path):
    script = OFFLINE / "build-bundle.sh"
    r = subprocess.run(
        ["bash", str(script)], capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "DRY_RUN": "1"},
    )
    assert r.returncode == 0, r.stderr
    assert "PLAN" in r.stdout and "MANIFEST.sha256" in r.stdout
    dist = OFFLINE / "dist"
    assert not dist.exists(), "DRY_RUN ne doit créer aucun artefact"


def test_07_install_bundle_exige_manifeste():
    t = (OFFLINE / "install-bundle.sh").read_text(encoding="utf-8")
    assert "sha256sum -c MANIFEST.sha256" in t, \
        "l'installateur doit refuser un paquet dont le manifeste échoue"
    assert "--no-index --find-links" in t, "installation pip hors-ligne attendue"


def test_08_readmes_racordes():
    r_setup = (SETUP / "README.md").read_text(encoding="utf-8")
    for i in range(11):
        assert f"{i:02d}-" in r_setup, f"README setup : script {i:02d} non documenté"
    r_off = (OFFLINE / "README.md").read_text(encoding="utf-8")
    assert "--no-index" in r_off and "MANIFEST.sha256" in r_off and "sha256sum -c" in r_off


def test_09_makefile_raccorde():
    mk = (ROOT / "Makefile").read_text(encoding="utf-8")
    for cible in ("setup-local", "setup-local-docker", "offline-bundle"):
        assert re.search(rf"^{cible}:.*##", mk, re.M), f"cible make absente : {cible}"
    r = subprocess.run(["make", "-n", "setup-local"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, f"make setup-local cassé : {r.stderr}"


def test_10_prereqs_verifie_les_outils_pivots():
    t = (SETUP / "00-prereqs.sh").read_text(encoding="utf-8")
    for outil in ("python3", "node", "npm", "docker", "openssl", "sha256sum"):
        assert outil in t, f"00-prereqs doit vérifier {outil}"
    assert "ALLOW_NO_DOCKER" in t, "l'échappatoire mode natif doit être explicite"
