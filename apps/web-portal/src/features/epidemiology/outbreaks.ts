/** Surveillance des éclosions TropiRAG — logique pure (testée sans React).
 *
 *  Transforme le snapshot GET /api/v1/surveillance/map (agrégats par district
 *  sanitaire CI, comptes 100 % déterministes — même source de vérité que
 *  l'export DHIS2) en structures d'affichage pour l'écran Épidémiologie. */

export interface TrSurveillance {
  window_days: number;
  total_cases: number;
  national_by_disease: Record<string, number>;
  districts: Array<{
    key: string; label: string; chief_town: string;
    cases: number; urgent: number; critical: number;
    by_disease: Record<string, number>; by_week: Record<string, number>;
    last_case_at: string | null;
  }>;
  non_localises: { cases: number; urgent: number; by_disease: Record<string, number> };
  outbreaks: Array<{
    district: string; label: string; last_week: string;
    cases_last_week: number; cases_previous_week: number; top_disease: string | null;
  }>;
  districts_meta: Array<{ key: string; label: string; chief_town: string; grid: [number, number] }>;
}

export interface TrMapTile {
  key: string;
  label: string;
  chief_town: string;
  col: number;          // 1-based pour CSS grid
  row: number;
  cases: number;
  urgent: number;
  critical: number;
  outbreak: boolean;
  tone: string;         // couleur de fond (alpha selon densité)
  title: string;        // tooltip complet
}

/** Intensité de couleur selon le nombre de cas (alpha bleu clinique). */
export function districtTone(cases: number): string {
  if (cases <= 0) return "transparent";
  const alpha = Math.min(0.14 + cases * 0.13, 0.88);
  return `rgba(45, 122, 179, ${alpha.toFixed(2)})`;
}

/** "2026W38" → "S38" (tolère les formats imprévus). */
export function weekLabel(week: string): string {
  const m = /W(\d+)/.exec(week || "");
  return m ? `S${m[1]}` : week;
}

/** Libellé maladie lisible (codes moteur → affichage). */
export const DISEASE_LABEL: Record<string, string> = {
  malaria: "paludisme",
  dengue: "dengue",
  zika: "zika",
  chikungunya: "chikungunya",
  yellow_fever: "fièvre jaune",
  typhoid: "typhoïde",
  leptospirosis: "leptospirose",
  meningitis: "méningite",
  cholera: "choléra",
  measles: "rougeole",
};

export function diseaseLabel(code: string | null | undefined): string {
  if (!code) return "—";
  return DISEASE_LABEL[code] ?? code;
}

/** Construit les 14 tuiles de la carte (districts actifs + muets). */
export function buildMapTiles(s: TrSurveillance): TrMapTile[] {
  const active = new Map(s.districts.map((d) => [d.key, d]));
  const outbreakKeys = new Set(s.outbreaks.map((o) => o.district));
  return s.districts_meta
    .map((meta) => {
      const d = active.get(meta.key);
      const cases = d?.cases ?? 0;
      const urgent = d?.urgent ?? 0;
      const critical = d?.critical ?? 0;
      const outbreak = outbreakKeys.has(meta.key);
      const top = d
        ? Object.entries(d.by_disease).sort((a, b) => b[1] - a[1])[0]?.[0]
        : undefined;
      return {
        key: meta.key,
        label: meta.label,
        chief_town: meta.chief_town,
        col: meta.grid[0] + 1,
        row: meta.grid[1] + 1,
        cases, urgent, critical, outbreak,
        tone: districtTone(cases),
        title: d
          ? `${meta.label} (${meta.chief_town}) — ${cases} cas` +
            (urgent ? `, ${urgent} urgence(s)` : "") +
            (critical ? `, ${critical} critique(s)` : "") +
            (top ? ` · suspect principal : ${diseaseLabel(top)}` : "") +
            (outbreak ? " · ⚠ SIGNAL D'ÉCLOSION" : "")
          : `${meta.label} (${meta.chief_town}) — aucun cas sur ${s.window_days} j`,
      };
    })
    .sort((a, b) => a.row - b.row || a.col - b.col);
}

/** Lignes textuelles des signaux d'éclosion (affichage + tests). */
export function outbreakLines(s: TrSurveillance): string[] {
  return s.outbreaks.map((o) => {
    const weeks = Object.keys(
      s.districts.find((d) => d.key === o.district)?.by_week ?? {},
    ).sort();
    const prevWeek = weeks.length >= 2 ? weeks[weeks.length - 2] : o.last_week;
    return `${o.label} — ${o.cases_last_week} cas ${weekLabel(o.last_week)}` +
      ` vs ${o.cases_previous_week} ${weekLabel(prevWeek)}` +
      ` · suspect principal : ${diseaseLabel(o.top_disease)}`;
  });
}

/** Résumé national : puce "paludisme 31", triée par fréquence décroissante. */
export function nationalChips(s: TrSurveillance): Array<{ label: string; n: number }> {
  return Object.entries(s.national_by_disease)
    .sort((a, b) => b[1] - a[1])
    .map(([code, n]) => ({ label: diseaseLabel(code), n }));
}
