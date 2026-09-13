"""Bootstrap pytest racine : rend les packages et services importables partout."""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
for p in ["packages/medisuite-core", "packages/clinical-rules"]:
    sys.path.insert(0, str(ROOT / p))
