import { describe, expect, it } from "vitest";
import {
  buildMapTiles, districtTone, diseaseLabel, nationalChips,
  outbreakLines, weekLabel, type TrSurveillance,
} from "./outbreaks";

const SNAP: TrSurveillance = {
  window_days: 30,
  total_cases: 31,
  national_by_disease: { malaria: 31, dengue: 26, zika: 8 },
  districts: [
    {
      key: "abidjan", label: "District d'Abidjan", chief_town: "Abidjan",
      cases: 14, urgent: 2, critical: 1,
      by_disease: { malaria: 8, dengue: 6 },
      by_week: { "2026W36": 3, "2026W37": 4, "2026W38": 7 },
      last_case_at: "2026-09-14T09:00:00",
    },
  ],
  non_localises: { cases: 2, urgent: 0, by_disease: { malaria: 2 } },
  outbreaks: [{
    district: "abidjan", label: "District d'Abidjan", last_week: "2026W38",
    cases_last_week: 7, cases_previous_week: 4, top_disease: "malaria",
  }],
  districts_meta: [
    { key: "abidjan", label: "District d'Abidjan", chief_town: "Abidjan", grid: [2, 3] },
    { key: "comoe", label: "Comoé", chief_town: "Aboisso", grid: [3, 3] },
    { key: "denguele", label: "Denguélé", chief_town: "Odienné", grid: [0, 0] },
  ],
};

describe("surveillance éclosions TropiRAG", () => {
  it("tonalité : transparent à 0 cas, intensifiée et plafonnée sinon", () => {
    expect(districtTone(0)).toBe("transparent");
    expect(districtTone(1)).toContain("0.27");
    expect(districtTone(99)).toContain("0.88"); // plafond d'alpha
  });

  it("libellé semaine ISO 2026W38 → S38", () => {
    expect(weekLabel("2026W38")).toBe("S38");
    expect(weekLabel("bizarre")).toBe("bizarre");
  });

  it("libellés maladies connues et repli brut", () => {
    expect(diseaseLabel("malaria")).toBe("paludisme");
    expect(diseaseLabel("yellow_fever")).toBe("fièvre jaune");
    expect(diseaseLabel("inconnue")).toBe("inconnue");
    expect(diseaseLabel(null)).toBe("—");
  });

  it("carte : 14 districts couverts, tuile d'éclosion marquée, muets à 0", () => {
    const tiles = buildMapTiles(SNAP);
    expect(tiles).toHaveLength(3);
    const abidjan = tiles.find((t) => t.key === "abidjan")!;
    expect(abidjan.cases).toBe(14);
    expect(abidjan.outbreak).toBe(true);
    expect(abidjan.title).toContain("SIGNAL D'ÉCLOSION");
    expect(abidjan.col).toBe(3);
    expect(abidjan.row).toBe(4);
    const denguele = tiles.find((t) => t.key === "denguele")!;
    expect(denguele.cases).toBe(0);
    expect(denguele.outbreak).toBe(false);
    expect(denguele.title).toContain("aucun cas sur 30 j");
  });

  it("lignes d'éclosion : dernière semaine vs précédente + suspect", () => {
    const lines = outbreakLines(SNAP);
    expect(lines).toEqual([
      "District d'Abidjan — 7 cas S38 vs 4 S37 · suspect principal : paludisme",
    ]);
  });

  it("puces nationales triées par fréquence décroissante", () => {
    expect(nationalChips(SNAP)).toEqual([
      { label: "paludisme", n: 31 },
      { label: "dengue", n: 26 },
      { label: "zika", n: 8 },
    ]);
  });
});
