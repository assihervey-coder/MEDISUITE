"""Événements de release (arbre conforme)."""
from ...domain.proposal.events import (RELEASE_CANDIDATE_CREATED, RELEASE_COMPLETED,  # noqa: F401
                                       ROLLOUT_ADVANCED, ROLLOUT_PAUSED,
                                       ROLLOUT_STARTED, ROLLBACK_COMPLETED,
                                       ROLLBACK_TRIGGERED, emit)
