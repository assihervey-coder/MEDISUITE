"""Exporteur DHIS2 — orchestre mapper → formats → file → transport."""
from __future__ import annotations

from tropirag.integrations.dhis2.mapper import Dhis2Mapper
from tropirag.integrations.dhis2.models import DataValueSet, ExportResult
from tropirag.integrations.dhis2.queue import OfflineQueue
from tropirag.integrations.dhis2.settings import Dhis2Config
from tropirag.integrations.dhis2.transport import (
    Dhis2Transport,
    PushReport,
    TransportNotConfigured,
)

FORMATS = ("json", "csv", "adx")


class Dhis2Exporter:
    """Point d'entrée unique de l'export DHIS2 (API + CLI partagent ceci)."""

    def __init__(self, cfg: Dhis2Config | None = None,
                 queue: OfflineQueue | None = None,
                 transport: Dhis2Transport | None = None) -> None:
        self.cfg = cfg or Dhis2Config()
        self.queue = queue or OfflineQueue(self.cfg.queue_path,
                                           self.cfg.queue_max_entries)
        self.transport = transport or Dhis2Transport(self.cfg)
        self.mapper = Dhis2Mapper(self.cfg)

    # ------------------------------------------------------------------
    def export(self, rows: list[dict], period: str,
               enqueue: bool | None = None) -> ExportResult:
        """Construit les valeurs de la période.

        ``enqueue`` : True = forcer la mise en file ; False = dry-run (rien
        n'est écrit) ; None (défaut) = suivre la configuration (mode
        offline_queue → file, mode push → envoi direct).
        """
        dvs: DataValueSet = self.mapper.map(rows, period)
        result = ExportResult(period=period, org_unit=self.cfg.org_unit,
                              counts=self.mapper.counts(rows),
                              data_values=dvs.data_values)
        if not self.cfg.enabled:
            result.notes.append("export désactivé (dhis2.enabled=false)")
            return result

        wants_queue = (enqueue is True) or (
            enqueue is None and self.cfg.mode == "offline_queue")
        if wants_queue and len(dvs):
            entry = self.queue.enqueue(dvs.to_json_payload(),
                                       meta={"period": period,
                                             "org_unit": self.cfg.org_unit,
                                             "values": len(dvs)})
            result.enqueued = True
            result.notes.append(f"payload {entry['id']} en file ({len(dvs)} valeurs)")

        if self.cfg.mode == "push" and len(dvs):
            try:
                report = self.transport.push(dvs.to_json_payload())
                result.pushed = report.ok
                result.notes.append(f"push: {'ok' if report.ok else 'échec'} "
                                    f"{report.status_code or ''}".strip())
            except TransportNotConfigured as e:
                result.notes.append(f"push impossible : {e}")
        return result

    # ------------------------------------------------------------------
    def render(self, dvs: DataValueSet, fmt: str) -> str:
        if fmt == "json":
            import json

            return json.dumps(dvs.to_json_payload(), ensure_ascii=False, indent=1)
        if fmt == "csv":
            return dvs.to_csv()
        if fmt == "adx":
            return dvs.to_adx()
        raise ValueError(f"format inconnu : {fmt} (attendus : {FORMATS})")

    # ------------------------------------------------------------------
    def flush_queue(self) -> list[PushReport]:
        """Tente l'envoi de toute la file pending (CLI/API explicites)."""
        reports: list[PushReport] = []
        for entry in self.queue.pending():
            try:
                report = self.transport.push(entry["payload"])
            except TransportNotConfigured as e:
                reports.append(PushReport(ok=False, detail=str(e)))
                break  # serveur absent : inutile d'insister
            self.queue.mark(entry["id"],
                            "sent" if report.ok else "failed",
                            note=report.detail)
            reports.append(report)
        return reports
