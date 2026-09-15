/** Tests du module DHIS2 (logique pure — semaine ISO, badges, synthèse). */
import { describe, expect, it } from "vitest";

import {
  currentIsoWeek, dhis2ModeLabel, dhis2QueueLine, exportSummaryRows,
  payloadStats, type Dhis2ExportResult, type Dhis2Status,
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
