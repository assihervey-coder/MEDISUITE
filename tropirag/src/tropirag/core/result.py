"""Résultats typés — pattern Result/Ok/Err pour éviter les exceptions métier."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class Ok(Generic[T]):
    value: T
    ok: bool = field(default=True, init=False)

    def unwrap(self) -> T:
        return self.value


@dataclass(slots=True)
class Err(Generic[T]):
    error: str
    code: str = "E_GENERIC"
    details: dict[str, Any] = field(default_factory=dict)
    ok: bool = field(default=False, init=False)

    def unwrap(self) -> T:
        raise RuntimeError(f"{self.code}: {self.error}")

    def to_dict(self) -> dict[str, Any]:
        return {"ok": False, "code": self.code, "error": self.error, "details": self.details}


Result = Ok[T] | Err[T]


def ok(value: T) -> Ok[T]:
    return Ok(value)


def err(error: str, code: str = "E_GENERIC", **details: Any) -> Err[T]:  # type: ignore[misc]
    return Err(error=error, code=code, details=details)  # type: ignore[arg-type]
