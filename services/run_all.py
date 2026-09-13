#!/usr/bin/env python3
"""Lance tous les services MEDISUITE en local (uvicorn, SQLite).

Usage : python3 services/run_all.py --up | --down | --status | --list
Chaque service démarre sur son port (services/registry.py), logs dans logs/.
"""
import argparse
import os
import pathlib
import signal
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "medisuite-core"))
sys.path.insert(0, str(ROOT / "packages" / "clinical-rules"))

from services.registry import ALL_SERVICES  # noqa: E402

PID_FILE = ROOT / "data" / "services.pid"
LOG_DIR = ROOT / "logs"


def _env(service: dict) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = (f"{ROOT / 'packages' / 'medisuite-core'}:"
                         f"{ROOT / 'packages' / 'clinical-rules'}:"
                         f"{ROOT / service['dir'] / 'src'}")
    env["MEDISUITE_PORT"] = str(service["port"])
    return env


def up(names: list[str] | None = None) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    (ROOT / "data").mkdir(exist_ok=True)
    targets = [s for s in ALL_SERVICES if not names or s["name"] in names]
    pids = _load_pids()
    started = 0
    for svc in targets:
        if svc["name"] in pids and _alive(pids[svc["name"]]):
            print(f"  ⏭  {svc['name']:<28} déjà actif (port {svc['port']})")
            continue
        log = open(LOG_DIR / f"{svc['name']}.log", "ab")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", svc["module"],
             "--host", "0.0.0.0", "--port", str(svc["port"]), "--log-level", "warning"],
            cwd=str(ROOT / svc["dir"]), env=_env(svc), stdout=log, stderr=log)
        pids[svc["name"]] = proc.pid
        started += 1
        print(f"  ▶  {svc['name']:<28} http://localhost:{svc['port']}/docs")
    _save_pids(pids)
    print(f"\n✅ {started} service(s) démarré(s). make smoke pour vérifier la santé.")


def down() -> None:
    pids = _load_pids()
    killed = 0
    for name, pid in pids.items():
        try:
            os.kill(pid, signal.SIGTERM)
            killed += 1
        except ProcessLookupError:
            pass
    PID_FILE.unlink(missing_ok=True)
    print(f"🛑 {killed} service(s) arrêté(s).")


def status() -> None:
    import urllib.request
    for svc in ALL_SERVICES:
        try:
            with urllib.request.urlopen(
                    f"http://localhost:{svc['port']}/health", timeout=1) as r:
                print(f"  ● {svc['name']:<28} :{svc['port']}  {r.status}")
        except Exception:
            print(f"  ○ {svc['name']:<28} :{svc['port']}  (inactif)")


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def _load_pids() -> dict[str, int]:
    if PID_FILE.exists():
        lines = PID_FILE.read_text().strip().splitlines()
        return {k: int(v) for k, v in (l.split("=") for l in lines if "=" in l)}
    return {}


def _save_pids(pids: dict[str, int]) -> None:
    PID_FILE.parent.mkdir(exist_ok=True)
    PID_FILE.write_text("\n".join(f"{k}={v}" for k, v in pids.items()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--up", action="store_true")
    ap.add_argument("--down", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--only", nargs="*", help="noms de services spécifiques")
    ap.add_argument("--group", choices=["core", "specialty", "transverse", "gateway"])
    args = ap.parse_args()
    names = args.only
    if args.group:
        names = [s["name"] for s in ALL_SERVICES if s["group"] == args.group]
    if args.up:
        up(names)
    elif args.down:
        down()
    else:
        status()
