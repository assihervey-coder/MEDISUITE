"""Cas d'usage — génération du dossier de preuve EVD-*."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...domain.proposal.value_objects import now_iso


def generate_evidence(evidence_dir: Path, subject: str, sections: dict[str, Any],
                      evidence_id: str | None = None) -> dict[str, Any]:
    """Assemble le dossier EVOLUTION EVIDENCE (13 sections attendues)."""
    expected = ["proposal", "impact-analysis", "risk-assessment", "architecture-diff",
                "approval", "implementation", "tests", "compatibility",
                "clinical-validation", "safety-validation", "deployment",
                "monitoring", "final-acceptance"]
    present = {k: v for k, v in sections.items() if v not in (None, {}, [])}
    missing = [s for s in expected if s not in present]
    record = {
        "evidence_id": evidence_id or f"EVD-{abs(hash(subject)) % 10000:04d}",
        "subject": subject, "created_at": now_iso(),
        "sections": present, "missing_sections": missing,
        "complete": not missing,
    }
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out = evidence_dir / f"{record['evidence_id']}.json"
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record
