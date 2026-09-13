"""Générateur des écrans fins du portal — 24 modules × 4 types = 96 écrans (v0.14).

Sources de vérité (aucune donnée clinique dupliquée à la main) :
- services/registry.py                    → 24 spécialités (n°, slug, libellé) ;
- apps/web-portal/src/features/modules-nav.ts → icônes + clés i18n `mod.*` ;
- services/<slug>/src/main.py             → ast : endpoints de score (docstring
  « Score <ep> — medisuite_rules.<mod> » + appel réel `mod.fn(**body)`) ;
- packages/clinical-rules                 → signatures inspectées (noms/types) ;
- ai/multimodal/configs/<NN>_<slug>.yaml  → tâche, modalités, heads, explicabilité ;
- datasets/registry.py                    → features (plages) + spec de label.

Sorties IDEMPOTENTES sous apps/web-portal/src/screens/ :
- registry.generated.ts  (96 ScreenDef : routes, scores, signatures, IA) ;
- routes.generated.tsx   (table SCREEN_ROUTES consommée par App.tsx) ;
- <urlSlug>/<Composant>.tsx (96 fichiers — un par écran, évolutables seuls).

Ne jamais éditer les fichiers *.generated.* ni les écrans générés à la main :
`make screens` régénère ; `tools/generate_screens.py --check` fait échouer la
CI en cas de dérive (même contrat que les model-cards v0.10).
"""
from __future__ import annotations

import ast
import importlib
import inspect
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "packages" / "clinical-rules"))

from services.registry import SPECIALTIES  # noqa: E402
from datasets.registry import SPEC  # noqa: E402

PORTAL = ROOT / "apps" / "web-portal" / "src" / "screens"
NAV_TS = ROOT / "apps" / "web-portal" / "src" / "features" / "modules-nav.ts"
CONFIGS = ROOT / "ai" / "multimodal" / "configs"

DOCRE = re.compile(r"^Score (\S+) — medisuite_rules\.(\w+)$")
NAVRE = re.compile(
    r'\{\s*to:\s*"/module/([a-z0-9-]+)",\s*slug:\s*"([a-z0-9_]+)",\s*icon:\s*"([^"]+)"\s*\}'
)

KINDS = (
    ("overview", "Overview"),
    ("cas", "CaseList"),
    ("detail", "CaseDetail"),
    ("ia", "AiAssist"),
)

HEADER = "/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — NE PAS ÉDITER À LA MAIN.\n *  Régénérer : `make screens` · vérifier : `python tools/generate_screens.py --check`.\n"


def pascal(slug: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[-_]", slug))


def parse_nav() -> dict[str, tuple[str, str]]:
    """urlSlug → (slug i18n, icône) depuis modules-nav.ts (source unique)."""
    out: dict[str, tuple[str, str]] = {}
    for m in NAVRE.finditer(NAV_TS.read_text(encoding="utf-8")):
        out[m.group(1)] = (m.group(2), m.group(3))
    return out


def score_endpoints(service_slug: str) -> list[tuple[str, str, str]]:
    """[(endpoint, module_règles, fn)] — depuis les docstrings + appels réels."""
    src = (ROOT / "services" / service_slug / "src" / "main.py").read_text(encoding="utf-8")
    eps: list[tuple[str, str, str]] = []
    for node in ast.parse(src).body:
        if not isinstance(node, ast.FunctionDef):
            continue
        m = DOCRE.match(ast.get_docstring(node) or "")
        if not m:
            continue
        ep, rmod = m.group(1), m.group(2)
        fn = None
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Attribute)
                and isinstance(sub.func.value, ast.Name)
                and sub.func.value.id == rmod
            ):
                fn = sub.func.attr
        eps.append((ep, rmod, fn or ""))
    return eps


def signature_of(rmod: str, fn: str) -> list[dict]:
    """[{name, kind, hasDefault}] — kind : number | text | boolean."""
    if not fn:
        return []
    mod = importlib.import_module(f"medisuite_rules.{rmod}")
    f = getattr(mod, fn, None)
    if f is None or not callable(f):
        return []
    out = []
    for name, p in inspect.signature(f).parameters.items():
        if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        ann = p.annotation
        kind = "boolean" if ann is bool else "number" if ann in (int, float) else "text"
        out.append({"name": name, "kind": kind, "hasDefault": p.default is not inspect.Parameter.empty})
    return out


def ai_info(module_no: int, slug_us: str) -> dict:
    cfg_path = CONFIGS / f"{module_no:02d}_{slug_us}.yaml"
    cfg = {}
    if cfg_path.exists():
        import yaml

        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    spec = SPEC.get(slug_us, {})
    feats = [
        {"name": n, "lo": r[0], "hi": r[1]} for n, r in spec.get("features", {}).items()
    ]
    label = spec.get("label", {})
    modalities = (cfg.get("modalities") or {})
    expl = [
        k for k, v in (cfg.get("explainability") or {}).items() if v
    ]
    return {
        "task": cfg.get("task") or label.get("task") or "n/d",
        "modalities": modalities.get("attendues") or [],
        "missingPolicy": modalities.get("politique_modalites_manquantes") or "n/d",
        "sharedTrunk": bool((cfg.get("heads") or {}).get("shared_trunk")),
        "explainability": expl,
        "labelTask": label.get("task") or "n/d",
        "labelNom": label.get("label_nom") or label.get("target_nom") or "",
        "classes": label.get("classes") or [],
        "features": feats,
    }


def build_screens() -> list[dict]:
    nav = parse_nav()
    if len(nav) != 24:
        raise SystemExit(f"modules-nav.ts : 24 entrées attendues, {len(nav)} trouvées")
    screens: list[dict] = []
    for module_no, service_slug, label in SPECIALTIES:
        url = service_slug[: -len("-service")]
        if url not in nav:
            raise SystemExit(f"module {url} absent de modules-nav.ts")
        slug_i18n, icon = nav[url]
        eps = score_endpoints(service_slug)
        sigs = [
            {"endpoint": ep, "fn": fn, "params": signature_of(rmod, fn)}
            for ep, rmod, fn in eps
        ]
        base = {"id": url, "slug": slug_i18n, "urlSlug": url, "moduleNo": module_no,
                "icon": icon, "label": label, "service": service_slug}
        ai = ai_info(module_no, slug_i18n)
        for kind, _comp in KINDS:
            route = {
                "overview": f"/module/{url}",
                "cas": f"/module/{url}/cas",
                "detail": f"/module/{url}/cas/:caseId",
                "ia": f"/module/{url}/ia",
            }[kind]
            screens.append({
                **base,
                "id": f"{url}:{kind}",
                "kind": kind,
                "route": route,
                "servicePath": f"module/{url}",
                "scores": [ep for ep, _m, _f in eps],
                "sigs": sigs,
                "ai": ai,
            })
    return screens


def ts_screen(s: dict) -> str:
    return json.dumps(s, ensure_ascii=False, indent=2)


def gen_registry(screens: list[dict]) -> str:
    body = ",\n".join("    " + ts_screen(s).replace("\n", "\n    ") for s in screens)
    return (
        HEADER + " */\n"
        'import type { ScreenDef } from "./types";\n\n'
        f"export const SCREENS: ScreenDef[] = [\n{body},\n];\n\n"
        'export function screenById(id: string): ScreenDef | undefined {\n'
        "  return SCREENS.find((s) => s.id === id);\n}\n\n"
        "export function screensOfModule(urlSlug: string): ScreenDef[] {\n"
        "  return SCREENS.filter((s) => s.urlSlug === urlSlug);\n}\n"
    )


def comp_of(s: dict) -> str:
    return pascal(s["urlSlug"]) + dict(KINDS)[s["kind"]]


def gen_routes(screens: list[dict]) -> str:
    imports = "\n".join(
        f'import {comp_of(s)} from "./{s["urlSlug"]}/{comp_of(s)}";'
        for s in screens
    )
    items = "\n".join(
        f'  {{ path: "{s["route"]}", element: <{comp_of(s)} /> }},' for s in screens
    )
    return (
        HEADER + " */\n"
        'import type { ReactNode } from "react";\n'
        f"{imports}\n\n"
        "/** Routes des 96 écrans fins — consommées par App.tsx (une seule map). */\n"
        "export const SCREEN_ROUTES: Array<{ path: string; element: ReactNode }> = [\n"
        f"{items}\n];\n"
    )


def gen_screen_file(s: dict) -> str:
    comp = dict(KINDS)[s["kind"]]
    tpl = {
        "overview": "OverviewScreen",
        "cas": "CaseListScreen",
        "detail": "CaseDetailScreen",
        "ia": "AiAssistScreen",
    }[s["kind"]]
    title = {
        "overview": "Vue d'ensemble du module",
        "cas": "Liste des cas cliniques",
        "detail": "Fiche cas clinique",
        "ia": "Assistance IA (non validée — R6-R8)",
    }[s["kind"]]
    fn = (
        "OverviewScreen" if s["kind"] == "overview"
        else "CaseListScreen" if s["kind"] == "cas"
        else "CaseDetailScreen" if s["kind"] == "detail"
        else "AiAssistScreen"
    )
    return (
        f"/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : {s['label']} · {title}.\n"
        f" *  Route : {s['route']} · service : {s['service']} (module {s['moduleNo']:02d}).\n"
        " *  Régénérer : `make screens` — ne pas éditer à la main. */\n"
        f'import {tpl} from "../templates/{tpl}";\n'
        'import { screenById } from "../registry.generated";\n\n'
        f"export default function {pascal(s['urlSlug'])}{comp}() {{\n"
        f'  return <{fn} screen={{screenById("{s["id"]}")!}} />;\n}}\n'
    )


def write_all(screens: list[dict]) -> list[Path]:
    written = []
    for path, content in outputs(screens):
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(path)
    return written


def outputs(screens: list[dict]) -> list[tuple[Path, str]]:
    out = [(PORTAL / "registry.generated.ts", gen_registry(screens)),
           (PORTAL / "routes.generated.tsx", gen_routes(screens))]
    for s in screens:
        comp = dict(KINDS)[s["kind"]]
        out.append((PORTAL / s["urlSlug"] / f"{pascal(s['urlSlug'])}{comp}.tsx",
                    gen_screen_file(s)))
    return out


def check(screens: list[dict]) -> int:
    drift = [p for p, c in outputs(screens)
             if not p.exists() or p.read_text(encoding="utf-8") != c]
    if drift:
        for p in drift:
            print(f"DRIFT: {p.relative_to(ROOT)}")
        print(f"--check : {len(drift)} fichier(s) dérivé(s) — relancer make screens")
        return 1
    print(f"--check OK : {len(screens)} écrans fins conformes à la régénération")
    return 0


def main() -> int:
    screens = build_screens()
    if "--check" in sys.argv:
        return check(screens)
    written = write_all(screens)
    print(f"{len(screens)} écrans fins (24 modules × 4 types) — {len(written)} fichier(s) écrit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
