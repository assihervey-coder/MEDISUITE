/** Intégration DHIS2 — logique pure (testée sans React).
 *
 *  Branche la surveillance d'éclosions TropiRAG sur le système national
 *  DHIS2 (MSP-CI) : statut de l'export (file offline / push), export
 *  hebdomadaire dataValueSets, file d'attente et envoi explicite.
 *  Comptes 100 % déterministes — aucune IA dans le comptage. */

export interface Dhis2Status {
  queue: {
    total: number; pending: number; sent?: number; failed?: number;
    by_status?: Record<string, number>;   // renvoyé par l'API (sent/failed dérivés)
    path?: string;
  };
  config: {
    mode: string;                    // off | offline_queue | push
    org_unit: string;
    transport_ready: boolean;
    elements_mapped: number;
  };
}

export interface Dhis2ExportResult {
  period: string;
  org_unit: string;
  rows_analyzed: number;
  counts: Record<string, number>;
  data_values: Array<{ de: string; value: number; period: string; org_unit: string }>;
  format: string;
  payload: string;
  enqueued: boolean;
  pushed: boolean;
  notes: string[];
}

export interface Dhis2PushResult {
  pushed?: number;
  failed?: number;
  detail?: string;
  details?: Array<{ ok: boolean; status_code: number | null; detail: string }>;
}

/** Semaine ISO courante au format DHIS2 « YYYYWww » (lundi = 1er jour). */
export function currentIsoWeek(d: Date = new Date()): string {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const day = t.getUTCDay() || 7;          // dimanche = 7
  t.setUTCDate(t.getUTCDate() + 4 - day);  // jeudi de la semaine ISO
  const yearStart = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((t.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return `${t.getUTCFullYear()}W${String(week).padStart(2, "0")}`;
}

/** Libellé du mode DHIS2 (badge du panneau). */
export function dhis2ModeLabel(status: Dhis2Status | null): string {
  if (!status) return "DHIS2 : ?";
  const mode = status.config.mode;
  if (mode === "push") {
    return status.config.transport_ready
      ? "DHIS2 : push activé (serveur configuré)"
      : "DHIS2 : push demandé — serveur non configuré";
  }
  if (mode === "offline_queue") {
    return "DHIS2 : file offline (aucun envoi implicite)";
  }
  return "DHIS2 : export désactivé";
}

/** Ligne de synthèse de la file d'attente (sent/failed dérivés de by_status). */
export function dhis2QueueLine(status: Dhis2Status | null): string {
  if (!status) return "";
  const q = status.queue;
  const by = q.by_status ?? {};
  const sent = q.sent ?? by["sent"] ?? 0;
  const failed = q.failed ?? by["failed"] ?? 0;
  return `file : ${q.pending} en attente · ${sent} envoyé(s) · ${failed} échec(s)`;
}

/** Libellés lisibles des indicateurs agrégés (clés logiques du dhis2.yaml). */
export const COUNT_LABEL: Record<string, string> = {
  total_cases: "Cas analysés",
  suspect_malaria: "Paludisme suspecté",
  suspect_severe_malaria: "Paludisme sévère",
  malaria_renal_rrt: "Paludisme + AKI (EER)",
  suspect_dengue: "Dengue suspectée",
  suspect_severe_dengue: "Dengue sévère",
  dengue_peds_critical: "Dengue pédiatrique critique",
  suspect_enteric_fever: "Typhoïde suspectée",
  typhoid_xdr: "Typhoïde XDR",
  suspect_yellow_fever: "Fièvre jaune suspectée",
  suspected_vhf: "Alertes FHV",
  suspect_leptospirosis: "Leptospirose",
  suspect_meningococcal: "IIM (méningocoque)",
  suspect_zika: "Zika",
  zika_pregnant: "Zika + grossesse",
  scd_fever: "Drépanocytose + fièvre",
  pregnancy_malaria: "Paludisme gestationnel",
  urgent_cases: "Cas urgents",
  critical_cases: "Cas critiques",
};

/** Lignes d'affichage de l'export : indicateur → valeur (zéros filtrés). */
export function exportSummaryRows(result: Dhis2ExportResult | null):
  Array<{ key: string; label: string; value: number }> {
  if (!result) return [];
  return Object.entries(result.counts)
    .filter(([key, v]) => v > 0 && key !== "total_cases")
    .map(([key, v]) => ({ key, label: COUNT_LABEL[key] ?? key, value: v }))
    .sort((a, b) => b.value - a.value);
}

/** Statistiques du payload dataValueSets rendu (aperçu avant envoi). */
export function payloadStats(payload: string): { values: number; ok: boolean } {
  try {
    const parsed = JSON.parse(payload) as { dataValues?: unknown[] };
    return { values: (parsed.dataValues ?? []).length, ok: true };
  } catch {
    return { values: 0, ok: false };
  }
}
