"""Impact Engine — agrège les 8 analyseurs sur les chemins modifiés réels."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import (ai_analyzer, api_analyzer, clinical_analyzer, code_analyzer,
               compliance_analyzer, database_analyzer, event_analyzer,
               security_analyzer)


@dataclass(slots=True)
class ImpactResult:
    files: int
    services: int
    databases: int
    apis: int
    events: int
    ai_models: int
    clinical_rules: int
    components: dict[str, int]
    details: dict[str, Any]

    def counts(self) -> dict[str, int]:
        return {
            "files": self.files, "services": self.services,
            "databases": self.databases, "apis": self.apis,
            "events": self.events, "ai_models": self.ai_models,
            "clinical_rules": self.clinical_rules,
        }


def analyze(changed_paths: list[str]) -> ImpactResult:
    code = code_analyzer.analyze_files(changed_paths)
    apis = api_analyzer.analyze_apis(changed_paths)
    dbs = database_analyzer.analyze_databases(changed_paths)
    evts = event_analyzer.analyze_events(changed_paths)
    clin = clinical_analyzer.analyze_clinical(changed_paths)
    ai = ai_analyzer.analyze_ai(changed_paths)
    sec = security_analyzer.analyze_security(changed_paths)
    comp = compliance_analyzer.analyze_compliance(changed_paths)

    details = {"code": code, "apis": apis, "databases": dbs, "events": evts,
               "clinical": clin, "ai": ai, "security": sec, "compliance": comp}
    ai_models = 1 if ai["count"] else 0
    clinical_rules = clin["count"]
    return ImpactResult(
        files=code["files"], services=code["services"],
        databases=dbs["databases"], apis=apis["count"],
        events=evts["count"], ai_models=ai_models,
        clinical_rules=clinical_rules,
        components=code["components"], details=details)
