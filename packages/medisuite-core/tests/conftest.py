"""Bootstrap : rend medisuite_core importable même sans le conftest racine.

(pyproject.toml local fait de packages/medisuite-core un rootdir pytest →
le conftest.py de la racine du dépôt n'est plus chargé.)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))
