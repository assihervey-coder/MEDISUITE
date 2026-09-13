"""ChangeType — référentiel des types de modification."""
from __future__ import annotations

ALLOWED = ("ADD", "MODIFY", "MIGRATE", "REMOVE")

# Type exige un plan de migration + rollback script
MIGRATION_KINDS = {"MIGRATE"}
# Type interdit sans compatibilité prouvée
RISKY_KINDS = {"REMOVE"}
