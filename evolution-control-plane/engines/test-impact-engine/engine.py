"""Test Impact Engine — façade."""
from __future__ import annotations

from .dependency_mapper import dependency_mapper  # noqa: F401
from .regression_selector import needs_full_regression  # noqa: F401
from .test_selector import select_tests  # noqa: F401
