"""Application FastAPI — Control Plane d'évolution MEDISUITE (port 8400).

Lancement :
    python -m evolution-control-plane.api.rest.app   # hyphens OK via runpy
ou  uvicorn avec import string (importlib gère les tirets).
"""
from __future__ import annotations

from ..._bridge import register

register()

import importlib  # noqa: E402

from fastapi import FastAPI  # noqa: E402

from . import assessments as _ass  # noqa: E402
from . import events as _evt  # noqa: E402
from . import proposals as _prop  # noqa: E402

_proposals_router = _prop.router
_assessments_router = _ass.assessments
_changes_router = _ass.changes
_validations_router = _ass.validations
_rollouts_router = _ass.rollouts
_rollbacks_router = _ass.rollbacks
_events_router = _evt.router


def create_app() -> FastAPI:
    app = FastAPI(
        title="MEDISUITE Evolution Control Plane",
        version="1.0.0",
        description="Gouvernance d'évolution : PROPOSITION → IMPACT → DÉCISION → "
                    "PLAN → IMPLÉMENTATION → VALIDATION → DÉPLOIEMENT → OBSERVATION "
                    "→ ACCEPTATION / ROLLBACK → PREUVE",
    )
    prefix = "/api/v1/evolution"
    app.include_router(_proposals_router, prefix=prefix)
    app.include_router(_assessments_router, prefix=prefix)
    app.include_router(_changes_router, prefix=prefix)
    app.include_router(_validations_router, prefix=prefix)
    app.include_router(_rollouts_router, prefix=prefix)
    app.include_router(_rollbacks_router, prefix=prefix)
    app.include_router(_events_router, prefix=prefix)

    @app.get("/api/v1/evolution/health")
    def health() -> dict:
        return {"status": "ok", "control_plane": "1.0.0", "principle": "NO DIRECT CHANGE"}

    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8400)
