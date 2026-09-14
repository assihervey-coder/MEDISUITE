"""Entités Patient — immuables, sans PII superflue."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.core.datetime import age_from_birthdate, parse_date_flexible
from tropirag.core.enums import PregnancyStatus, Sex


@dataclass(slots=True)
class Patient:
    """Patient vu en consultation — strict minimum clinique, anonymisable."""

    local_id: str | None = None
    age_years: int | None = None
    age_months: int | None = None  # nourrissons
    sex: Sex = Sex.UNKNOWN
    pregnant: PregnancyStatus = PregnancyStatus.NOT_APPLICABLE
    gestational_age_weeks: int | None = None  # terme en semaines d'aménorrhée
    weight_kg: float | None = None
    known_allergies: list[str] = field(default_factory=list)
    chronic_conditions: list[str] = field(default_factory=list)  # drépanocytose, VIH, diabète...
    current_medications: list[str] = field(default_factory=list)
    birthdate: object | None = None  # date optionnelle

    @classmethod
    def from_dict(cls, data: dict) -> "Patient":
        birth = parse_date_flexible(data.get("birthdate"))
        age = data.get("age_years")
        if age is None and birth is not None:
            age = age_from_birthdate(birth)
        ga = data.get("gestational_age_weeks")
        return cls(
            local_id=data.get("patient_id"),
            age_years=age,
            age_months=data.get("age_months"),
            sex=Sex(data.get("sex", "unknown")),
            pregnant=PregnancyStatus(data.get("pregnant", "not_applicable")),
            gestational_age_weeks=int(ga) if ga is not None else None,
            weight_kg=data.get("weight_kg"),
            known_allergies=list(data.get("known_allergies") or []),
            chronic_conditions=list(data.get("chronic_conditions") or []),
            current_medications=list(data.get("current_medications") or []),
            birthdate=birth,
        )

    def is_child(self) -> bool:
        return (self.age_years is not None and self.age_years < 15) or (
            self.age_years is None and self.age_months is not None
        )

    def is_infant(self) -> bool:
        return self.age_years is not None and self.age_years < 1 or (
            self.age_years in (None, 0) and self.age_months is not None
        )

    def is_pregnant_or_possible(self) -> bool:
        return self.pregnant in (
            PregnancyStatus.PREGNANT,
            PregnancyStatus.POSSIBLY_PREGNANT,
        )

    def has_condition(self, needle: str) -> bool:
        """Recherche insensible à la casse ET aux accents (FR terrain)."""
        import unicodedata

        def _strip(s: str) -> str:
            t = unicodedata.normalize("NFKD", s.lower())
            return "".join(c for c in t if not unicodedata.combining(c))

        needle_l = _strip(needle)
        return any(needle_l in _strip(c) for c in self.chronic_conditions)

    def is_female_childbearing(self) -> bool:
        from tropirag.core.enums import Sex as _S

        return self.sex == _S.FEMALE and (
            self.age_years is None or 12 <= self.age_years <= 55
        )

    # --- grossesse (V1.1) ------------------------------------------------------

    def is_first_trimester(self) -> bool:
        """1er trimestre : < 14 semaines d'aménorrhée."""
        return self.is_pregnant_or_possible() and self.gestational_age_weeks is not None \
            and self.gestational_age_weeks < 14

    def is_second_trimester(self) -> bool:
        """2e trimestre : 14–27 SA inclus."""
        return self.is_pregnant_or_possible() and self.gestational_age_weeks is not None \
            and 14 <= self.gestational_age_weeks <= 27

    def is_third_trimester(self) -> bool:
        """3e trimestre : ≥ 28 SA."""
        return self.is_pregnant_or_possible() and self.gestational_age_weeks is not None \
            and self.gestational_age_weeks >= 28

    # --- drépanocytose (V1.1) ---------------------------------------------------

    def has_sickle_cell_disease(self) -> bool:
        """Drépanocytose (SS, SC, Sβ-thalassémie) — pas le simple trait AS."""
        return self.has_condition("drépano") or self.has_condition("sickle")
