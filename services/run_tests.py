#!/usr/bin/env python3
"""Exécute les tests de tous les services (chaque service = suite pytest isolée)."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    services_root = ROOT / "services"
    suites = sorted(p for p in services_root.glob("*/tests")
                    if any(p.glob("test_*.py")))
    if not suites:
        print("Aucune suite de tests trouvée.")
        return 0
    failures: list[str] = []
    passed = 0
    for suite in suites:
        name = suite.parent.name
        # BDD fraîche à chaque exécution → suites idempotentes
        db = ROOT / "data" / f"{name}.db"
        for suffix in ("", "-wal", "-shm"):
            (pathlib.Path(str(db) + suffix)).unlink(missing_ok=True)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(suite), "-q", "--no-header"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=300)
        tail = result.stdout.strip().splitlines()[-1] if result.stdout else "?"
        if result.returncode == 0:
            passed += 1
            print(f"  ✅ {name:<28} {tail}")
        else:
            failures.append(name)
            print(f"  ❌ {name:<28} {tail}")
            print("     " + "\n     ".join(
                result.stdout.strip().splitlines()[-8:]))
    print(f"\n{'=' * 60}\n{passed}/{len(suites)} suites vertes."
          + (f" Échecs : {failures}" if failures else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
