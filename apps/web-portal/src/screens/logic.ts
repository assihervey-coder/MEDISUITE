/** Logique PURE des écrans fins (v0.14) — testée sans React (vitest).
 *  Aucun effet de bord : mêmes entrées → mêmes sorties, partout. */
import type { CaseRow, ParamKind, ScreenDef } from "./types";

/** Sévérités considérées critiques pour le KPI dédié (fr + en). */
const SEVERES = new Set([
  "haute",
  "critique",
  "élevée",
  "elevée",
  "elevee",
  "high",
  "critical",
  "severe",
]);

export function isSevere(severite?: string): boolean {
  return severite !== undefined && SEVERES.has(severite.trim().toLowerCase());
}

/** Filtre de la liste des cas : requête (titre/patient), statut, sévérité. */
export function filterCases(
  cases: CaseRow[],
  query: string,
  statut: string,
  severite: string,
): CaseRow[] {
  const q = query.trim().toLowerCase();
  return cases.filter((c) => {
    if (statut !== "" && (c.statut ?? "") !== statut) return false;
    if (severite !== "" && (c.severite ?? "") !== severite) return false;
    if (q === "") return true;
    const hay = `${c.titre} ${c.patient_nom ?? ""} ${c.patient_id ?? ""}`.toLowerCase();
    return hay.includes(q);
  });
}

/** Valeurs distinctes non vides d'un champ (pour les <select> de filtre). */
export function distinct(cases: CaseRow[], field: "statut" | "severite"): string[] {
  const seen = new Set<string>();
  for (const c of cases) {
    const v = (c[field] ?? "").trim();
    if (v !== "") seen.add(v);
  }
  return [...seen].sort((a, b) => a.localeCompare(b));
}

/** KPI de la vue d'ensemble — comptages dérivés, aucune donnée fabriquée. */
export function computeKpis(cases: CaseRow[]): {
  total: number;
  actifs: number;
  clos: number;
  severe: number;
} {
  const actifs = cases.filter((c) => (c.statut ?? "actif") !== "clos").length;
  return {
    total: cases.length,
    actifs,
    clos: cases.length - actifs,
    severe: cases.filter((c) => isSevere(c.severite)).length,
  };
}

/** Type d'input HTML pour un paramètre de score. */
export function paramInputKind(kind: ParamKind): "number" | "text" | "checkbox" {
  return kind === "boolean" ? "checkbox" : kind;
}

/** Routes sœurs d'un module (tabs de la vue d'ensemble, retour, lien cas). */
export function siblingRoute(screen: ScreenDef, kind: ScreenDef["kind"]): string {
  switch (kind) {
    case "overview":
      return `/module/${screen.urlSlug}`;
    case "cas":
      return `/module/${screen.urlSlug}/cas`;
    case "ia":
      return `/module/${screen.urlSlug}/ia`;
    case "detail":
      return `/module/${screen.urlSlug}/cas`;
  }
}

/** Corps de requête typé pour un endpoint de score (valeurs d'inputs).
 *  Les booléens sont TOUJOURS envoyés (false est significatif) ; les champs
 *  vides sont omis — le défaut serveur s'applique, sinon 422 explicite. */
export function buildScoreBody(
  params: Array<{ name: string; kind: ParamKind; hasDefault: boolean }>,
  values: Record<string, string | boolean>,
): Record<string, unknown> {
  const body: Record<string, unknown> = {};
  for (const p of params) {
    const v = values[p.name];
    if (p.kind === "boolean") {
      body[p.name] = v === true;
      continue;
    }
    if (v === undefined || v === "") continue;
    body[p.name] = p.kind === "number" ? Number(v) : v;
  }
  return body;
}
