"""Unit of Work — transaction atomique sur les dépôts, rollback garanti.

Usage :
    with UnitOfWork(db) as uow:
        uow.cases.save_case(...)
        uow.patients.upsert(...)
        uow.inference.log(...)
    # commit en sortie normale, rollback en exception
"""
from __future__ import annotations

from tropirag.persistence.database import Database
from tropirag.persistence.repositories.audit_repository import AuditRepository
from tropirag.persistence.repositories.case_repository import CaseRepository
from tropirag.persistence.repositories.evidence_repository import EvidenceRepository
from tropirag.persistence.repositories.model_repository import ModelRepository
from tropirag.persistence.repositories.patient_repository import PatientRepository


class UnitOfWork:
    """Point d'accès unique aux repositories — frontière transactionnelle."""

    def __init__(self, db: Database | None = None) -> None:
        self.db = db or Database.instance()
        self.cases = CaseRepository(self.db)
        self.patients = PatientRepository(self.db)
        self.evidence = EvidenceRepository(self.db)
        self.models = ModelRepository(self.db)
        self.audits = AuditRepository(self.db)
        self._own_transaction = False

    # ------------------------------------------------------------------
    def __enter__(self) -> "UnitOfWork":
        self.db.begin()
        self._own_transaction = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self._own_transaction:
            return
        if exc_type is None:
            self.db.commit()
        else:
            self.db.rollback()
        self._own_transaction = False

    # ------------------------------------------------------------------
    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
