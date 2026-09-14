"""Socle commun de l'évaluation — métriques, datasets, rapports.

Aucune dépendance externe (stdlib pure) : l'évaluation doit tourner en mode
offline complet, comme le système lui-même.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

EVAL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

REPORTS_DIR = EVAL_ROOT / "reports"
DATASETS_DIR = EVAL_ROOT / "datasets"


# ---------------------------------------------------------------------------
# Contrats
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class MetricResult:
    """Une métrique nommée avec seuil et verdict."""
    name: str
    value: float
    threshold: float
    details: dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.value >= self.threshold


@dataclass(slots=True)
class SuiteReport:
    """Rapport d'une suite d'évaluation."""
    suite: str
    metrics: list[MetricResult] = field(default_factory=list)
    cases: list[dict] = field(default_factory=list)   # détails par cas
    generated_at: str = ""
    passed: bool = True

    def add(self, metric: MetricResult) -> MetricResult:
        self.metrics.append(metric)
        if not metric.passed:
            self.passed = False
        return metric

    @property
    def as_dict(self) -> dict:
        return {
            "suite": self.suite,
            "generated_at": self.generated_at,
            "passed": self.passed,
            "metrics": [
                {"name": m.name, "value": m.value, "threshold": m.threshold,
                 "passed": m.passed, "details": m.details}
                for m in self.metrics
            ],
            "cases": self.cases,
        }


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_dataset(name: str) -> list[dict]:
    """Charge tous les JSON d'un dataset (clinical_cases, adversarial_cases…)."""
    directory = DATASETS_DIR / name
    if not directory.exists():
        return []
    out = []
    for f in sorted(directory.glob("*.json")):
        out.append(load_json(f))  # type: ignore[arg-type]
    return out


# ---------------------------------------------------------------------------
# Rapports
# ---------------------------------------------------------------------------


def write_report(report: SuiteReport, markdown: str = "") -> Path:
    """Écrit le rapport JSON + Markdown de la suite — evaluation/reports/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report.generated_at = report.generated_at or time.strftime("%Y-%m-%dT%H:%M:%S")
    suite_dir = REPORTS_DIR / report.suite
    suite_dir.mkdir(parents=True, exist_ok=True)
    json_path = suite_dir / f"{report.suite}_report.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report.as_dict, fh, ensure_ascii=False, indent=2)
    if markdown:
        md_path = suite_dir / f"{report.suite}_report.md"
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(markdown)
    return json_path


def markdown_summary(report: SuiteReport) -> str:
    """Tableau Markdown du rapport — pour lecture humaine / gouvernance."""
    lines = [f"# Rapport d'évaluation — {report.suite}",
             f"Généré : {report.generated_at}", ""]
    lines.append("| Métrique | Valeur | Seuil | Verdict |")
    lines.append("|---|---|---|---|")
    for m in report.metrics:
        verdict = "✓ PASS" if m.passed else "✗ FAIL"
        lines.append(f"| {m.name} | {m.value:.4f} | {m.threshold:.2f} | {verdict} |")
    lines.append("")
    lines.append(f"**Verdict global : {'PASS' if report.passed else 'FAIL'}**")
    return "\n".join(lines)
