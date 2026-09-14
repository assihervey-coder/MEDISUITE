"""Utilitaires temporels : dates locales, parse flexible, âge, durées."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

try:  # zoneinfo est stdlib
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]

DEFAULT_TZ = "Africa/Abidjan"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def local_now(tz_name: str = DEFAULT_TZ) -> datetime:
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo(tz_name))
        except Exception:
            pass
    return datetime.now(timezone.utc)


def parse_date_flexible(value: str | date | datetime | None) -> date | None:
    """Parse ISO, YYYY-MM-DD, DD/MM/YYYY, ou renvoie None."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    fmts = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y")
    for f in fmts:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    return None


_DURATION_RE = re.compile(
    r"^\s*(?P<n>\d+(?:\.\d+)?)\s*(?P<unit>jours?|j|days?|d|semaines?|w|heures?|h|hours?|mois|months?|m)",
    re.IGNORECASE,
)


@dataclass(slots=True)
class Duration:
    days: float

    def hours(self) -> float:
        return self.days * 24.0

    def __str__(self) -> str:
        if self.days >= 7 and self.days % 7 == 0:
            return f"{int(self.days // 7)} sem."
        if self.days >= 1:
            return f"{int(self.days)} j"
        return f"{int(self.hours())} h"


def parse_duration(value: str | int | float | None) -> Duration | None:
    """Parse « 5 jours », « 48h », « 2 semaines », « 3 mois », ou nombre = jours."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return Duration(days=float(value))
    m = _DURATION_RE.match(str(value))
    if not m:
        try:
            return Duration(days=float(value))
        except ValueError:
            return None
    n = float(m.group("n"))
    u = m.group("unit").lower()
    if u.startswith(("h", "heures")):
        return Duration(days=n / 24.0)
    if u.startswith(("s", "w")) and not u.startswith("sem"):  # 'weeks'
        return Duration(days=n * 7)
    if u.startswith("sem"):
        return Duration(days=n * 7)
    if u.startswith("moi"):
        return Duration(days=n * 30.4)
    return Duration(days=n)


def days_between(a: date | None, b: date | None) -> float | None:
    if a is None or b is None:
        return None
    return (b - a).days


def age_from_birthdate(birthdate: date | None, ref: date | None = None) -> int | None:
    if birthdate is None:
        return None
    ref = ref or local_now().date()
    return ref.year - birthdate.year - ((ref.month, ref.day) < (birthdate.month, birthdate.day))


def within_window(delta_days: float | None, lo: float | None, hi: float | None) -> bool:
    """delta ∈ [lo, hi] ; bornes None = ouvertes ; delta None = False."""
    if delta_days is None:
        return False
    if lo is not None and delta_days < lo:
        return False
    if hi is not None and delta_days > hi:
        return False
    return True


def iso(d: date | datetime | None) -> str | None:
    return d.isoformat() if d else None
