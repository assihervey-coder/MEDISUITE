#!/usr/bin/env python3
"""Extrait les données d'audit des 26 modules → JSON pour docs/audit-26-modules.md."""
import json
import pathlib
import re

ROOT = pathlib.Path("/home/z/my-project/medisuite")

# Slugs depuis registry.py (SPECIALTIES) + cœur
reg = (ROOT / "services" / "registry.py").read_text()
specialties = re.findall(r'\((\d+),\s*"([\w-]+)",', reg)
slugs = [("1", "imaging"), ("2", "laboratory")] + specialties

out = []
for no, svc_slug in slugs:
    if not svc_slug.endswith("-service"):
        svc_slug += "-service"  # cœur : imaging, laboratory
    slug = svc_slug.replace("-service", "")  # datasets/configs : sans suffixe
    d = ROOT / "services" / svc_slug
    main_txt = (d / "src/main.py").read_text()
    m = re.search(r'"scores":\s*\[(.*?)\]', main_txt, re.S)
    scores = [x.strip().strip(" '\",") for x in m.group(1).split(",")] if m else []
    mod_m = re.search(r'"module":\s*(\d+)', main_txt)
    no_real = int(mod_m.group(1)) if mod_m else int(no)
    test_txt = (d / "tests" / f"test_{slug}.py").read_text()
    n_tests = len(re.findall(r"^def test_", test_txt, re.M))
    cfg = list((ROOT / "ai/multimodal/configs").glob(f"{no_real:02d}_*.yaml"))
    cfg_name = cfg[0].name if cfg else None
    ds_slug = slug.replace("-", "_")  # datasets : nuclear_medicine
    train = sum(1 for _ in open(ROOT / "datasets" / ds_slug / "train.jsonl"))
    out.append({"no": no_real, "slug": slug, "scores": scores, "n_scores": len(scores),
                "loc": len(main_txt.splitlines()), "n_tests": n_tests,
                "config_ia": cfg_name, "n_train": train})

out.sort(key=lambda x: x["no"])
dest = ROOT / "docs" / "_audit_data.json"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"{len(out)} modules → {dest}")
for o in out:
    print(f'{o["no"]:>2} {o["slug"]:<22} scores={o["n_scores"]:>2} tests={o["n_tests"]:>2} '
          f'loc={o["loc"]:>3} cfg={o["config_ia"]} train={o["n_train"]}')
