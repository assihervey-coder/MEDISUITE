/** Tests du module DHIS2 (logique pure — semaine ISO, badges, synthèse). */
import { describe, expect, it } from "vitest";

import {
  cronLabel, currentIsoWeek, dhis2ModeLabel, dhis2QueueLine, exportSummaryRows,
  lastRunLabel, payloadStats, type Dhis2CronStatus, type Dhis2ExportResult,
  type Dhis2Status,
} from "./dhis2";

const status = (over: Partial<Dhis2Status> = {}): Dhis2Status => ({
  queue: { total: 3, pending: 2, sent: 1, failed: 0 },
  config: { mode: "offline_queue", org_unit: "OU-CI-TEST",
            transport_ready: false, elements_mapped: 19 },
  ...over,
});

describe("currentIsoWeek", () => {
  it("donne la semaine ISO du mardi 15 sept 2026 → 2026W38", () => {
    expect(currentIsoWeek(new Date(2026, 8, 15))).toBe("2026W38");
  });
  it("lundi 30 déc 2024 appartient à 2025W01 (règle ISO du jeudi)", () => {
    expect(currentIsoWeek(new Date(2024, 11, 30))).toBe("2025W01");
  });
  it("dimanche 4 janv 2026 clôt la semaine 2026W01", () => {
    expect(currentIsoWeek(new Date(2026, 0, 4))).toBe("2026W01");
  });
  it("padStart : semaine 3 → W03", () => {
    expect(currentIsoWeek(new Date(2026, 0, 14))).toBe("2026W03"); // mer 14 janv
  });
});

describe("dhis2ModeLabel", () => {
  it("file offline par défaut", () => {
    expect(dhis2ModeLabel(status())).toBe("DHIS2 : file offline (aucun envoi implicite)");
  });
  it("push avec serveur configuré", () => {
    expect(dhis2ModeLabel(status({ config: {
      mode: "push", org_unit: "OU", transport_ready: true, elements_mapped: 19 } })))
      .toBe("DHIS2 : push activé (serveur configuré)");
  });
  it("push demandé sans serveur", () => {
    expect(dhis2ModeLabel(status({ config: {
      mode: "push", org_unit: "OU", transport_ready: false, elements_mapped: 19 } })))
      .toBe("DHIS2 : push demandé — serveur non configuré");
  });
  it("inconnu si statut absent", () => {
    expect(dhis2ModeLabel(null)).toBe("DHIS2 : ?");
  });
});

describe("dhis2QueueLine", () => {
  it("résume la file (champs directs)", () => {
    expect(dhis2QueueLine(status())).toBe("file : 2 en attente · 1 envoyé(s) · 0 échec(s)");
  });
  it("dérive sent/failed de by_status (format API réel)", () => {
    expect(dhis2QueueLine(status({
      queue: { total: 3, pending: 0, by_status: { sent: 2, failed: 1 } },
    }))).toBe("file : 0 en attente · 2 envoyé(s) · 1 échec(s)");
  });
});

describe("cronLabel / lastRunLabel", () => {
  const cron = (over: Partial<Dhis2CronStatus> = {}): Dhis2CronStatus => ({
    config: { auto: "push", day: "MON", hour_utc: 6 },
    state: {},
    next_run: "2026-09-21T06:00:00+00:00",
    period_exported: "2026W37",
    ...over,
  });

  it("push → planning + mode", () => {
    expect(cronLabel(cron()))
      .toBe("Envoi hebdo automatique : lundi 06:00 UTC (export + push serveur)");
  });
  it("queue → planning sans réseau", () => {
    expect(cronLabel(cron({ config: { auto: "queue", day: "SUN", hour_utc: 22 } })))
      .toBe("Export hebdo automatique : dimanche 22:00 UTC (en file, sans envoi réseau)");
  });
  it("off → désactivé", () => {
    expect(cronLabel(cron({ config: { auto: "off", day: "MON", hour_utc: 6 } })))
      .toBe("Envoi hebdo automatique : désactivé (push manuel via l'UI)");
  });
  it("dernier cycle planifié", () => {
    const c = cron({ state: { ran_at: "2026-09-21T06:00:10+00:00",
                              period: "2026W37", values: 4, pushed: 1, ok: true } });
    expect(lastRunLabel(c)).toBe(
      "Dernier cycle (planifié) : 2026W37 — 4 valeur(s), 1 payload(s) poussé(s) · succès");
  });
  it("dernier cycle manuel (imbriqué), échec", () => {
    const c = cron({ state: { last_manual_run: { ran_at: "2026-09-15T05:37:55+00:00",
                                                 period: "2026W37", values: 4,
                                                 pushed: 0, ok: false } } });
    expect(lastRunLabel(c)).toContain("Dernier cycle (manuel) : 2026W37");
    expect(lastRunLabel(c)).toContain("échec/partiel");
  });
  it("aucun cycle", () => {
    expect(lastRunLabel(cron())).toBe("Aucun cycle exécuté à ce jour");
    expect(lastRunLabel(null)).toBe("");
  });
});

describe("exportSummaryRows", () => {
  const result: Dhis2ExportResult = {
    period: "2026W38", org_unit: "OU-CI-TEST", rows_analyzed: 9,
    counts: { total_cases: 9, suspect_malaria: 7, suspect_dengue: 2, urgent_cases: 0 },
    data_values: [], format: "json", payload: "{}", enqueued: true, pushed: false,
    notes: [],
  };
  it("filtre les zéros et le total, trie par valeur décroissante", () => {
    expect(exportSummaryRows(result)).toEqual([
      { key: "suspect_malaria", label: "Paludisme suspecté", value: 7 },
      { key: "suspect_dengue", label: "Dengue suspectée", value: 2 },
    ]);
  });
  it("clé inconnue : affichée brute", () => {
    expect(exportSummaryRows({ ...result,
      counts: { anomalie_inconnue: 4 } as Record<string, number> }))
      .toEqual([{ key: "anomalie_inconnue", label: "anomalie_inconnue", value: 4 }]);
  });
  it("résultat absent → aucune ligne", () => {
    expect(exportSummaryRows(null)).toEqual([]);
  });
});

describe("payloadStats", () => {
  it("compte les dataValues d'un payload DHIS2", () => {
    expect(payloadStats('{"dataValues":[{"de":"DE1","value":7}]}'))
      .toEqual({ values: 1, ok: true });
  });
  it("payload non JSON → non valide", () => {
    expect(payloadStats("<adx/>")).toEqual({ values: 0, ok: false });
  });
});
