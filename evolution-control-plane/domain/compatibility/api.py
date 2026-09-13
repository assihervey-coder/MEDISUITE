"""Vérificateur de compatibilité API — signatures/chemins publics."""
from __future__ import annotations


class ApiCompat:
    dimension = "api"

    def check(self, endpoints_before: dict[str, str],
              endpoints_after: dict[str, str]) -> tuple[str, str]:
        """{chemin: signature} — un endpoint public retiré ou re-signé = REVIEW_REQUIRED."""
        removed = sorted(set(endpoints_before) - set(endpoints_after))
        changed = sorted(k for k in set(endpoints_before) & set(endpoints_after)
                         if endpoints_before[k] != endpoints_after[k])
        if removed or changed:
            return "REVIEW_REQUIRED", (
                f"endpoints retirés : {removed or '—'} ; re-signés : {changed or '—'}")
        added = sorted(set(endpoints_after) - set(endpoints_before))
        return "PASS", f"additif uniquement ({len(added)} ajout(s))"


class DatabaseCompat:
    dimension = "database"

    def check(self, drop_columns: list[str], expand_only: bool) -> tuple[str, str]:
        if drop_columns:
            return "FAIL", ("DROP direct interdit — stratégie expand/migrate/contract "
                            f"(colonnes visées : {drop_columns})")
        if expand_only:
            return "PASS", "migration additive (expand) sans retrait"
        return "REVIEW_REQUIRED", "migration non triviale : plan expand/migrate/contract requis"


class EventCompat:
    dimension = "events"

    def check(self, events_before: set[str], events_after: set[str]) -> tuple[str, str]:
        removed = sorted(events_before - events_after)
        if removed:
            return "REVIEW_REQUIRED", f"événements retirés : {removed}"
        return "PASS", f"{len(events_after - events_before)} nouvel(aux) événement(s)"


class FhirCompat:
    dimension = "fhir"

    def check(self, profiles_changed: list[str], r6_isolated: bool = True) -> tuple[str, str]:
        if not profiles_changed:
            return "NOT_APPLICABLE", "aucun profil FHIR touché"
        if r6_isolated:
            return "REVIEW_REQUIRED", (
                f"profils modifiés {profiles_changed} — périmètre R6 eCRF isolé (ADR-0024), "
                "revue interop requise")
        return "WARNING", "profils modifiés sans isolation R6 confirmée"


class DicomCompat:
    dimension = "dicom"

    def check(self, sop_classes_changed: bool) -> tuple[str, str]:
        if sop_classes_changed:
            return "FAIL", "changement de SOP class DICOM — flux PACS/DICOMweb rompu"
        return "NOT_APPLICABLE", "DICOM inchangé"


class Hl7Compat:
    dimension = "hl7"

    def check(self, segments_changed: list[str]) -> tuple[str, str]:
        if segments_changed:
            return "REVIEW_REQUIRED", f"segments HL7 modifiés : {segments_changed}"
        return "NOT_APPLICABLE", "HL7 inchangé"


class AiCompat:
    dimension = "ai"

    def check(self, model_changed: bool, lineage_complete: bool,
              threshold_changed: bool = False) -> tuple[str, str]:
        if not model_changed and not threshold_changed:
            return "NOT_APPLICABLE", "aucun modèle/seuil touché"
        if not lineage_complete:
            return "WARNING", "lineage incomplet (template AI_PROPOSAL : 11 versions exigées)"
        if threshold_changed:
            return "REVIEW_REQUIRED", "changement de seuil décisionnel → gate P8"
        return "PASS", "lineage complet, seuils inchangés"
