import { describe, expect, it } from "vitest";
import {
  addMonths,
  BANNER_TEXT,
  countdownLabel,
  daysBetween,
  m18Date,
  m18Status,
  M0,
  OUTPUT_STAMP,
  stampIsInvestigational,
} from "./investigation";

describe("calendrier M+", () => {
  it("addMonths plafonne la fin de mois (31/02 → 28/02)", () => {
    expect(addMonths(new Date(2025, 0, 31), 1)).toEqual(new Date(2025, 1, 28));
    expect(addMonths(new Date(2024, 0, 31), 1)).toEqual(new Date(2024, 1, 29)); // bissextile
  });

  it("le verrou M+18 tombe 18 mois pleins après M0", () => {
    expect(m18Date(M0)).toEqual(new Date(2026, 11, 1)); // 2026-12-01
    expect(m18Date(new Date(2026, 0, 31))).toEqual(new Date(2027, 6, 31));
  });

  it("daysBetween compte des jours pleins", () => {
    expect(daysBetween(new Date(2026, 11, 1), new Date(2025, 5, 1))).toBe(548);
    expect(daysBetween(new Date(2026, 11, 1), new Date(2026, 11, 1))).toBe(0);
  });
});

describe("état du verrou M+18", () => {
  it("avant le verrou : phase R6, décision interdite, J−x cohérent", () => {
    const st = m18Status(new Date(2026, 8, 15), M0); // 2026-09-15
    expect(st.pose).toBe(false);
    expect(st.phaseActive).toBe("R6");
    expect(st.verrouIso).toBe("2026-12-01");
    expect(st.joursAvantVerrou).toBe(77);
    expect(st.moisEcoules).toBe(15);
  });

  it("le jour du verrou : posé, J−0", () => {
    const st = m18Status(new Date(2026, 11, 1), M0);
    expect(st.pose).toBe(true);
    expect(st.joursAvantVerrou).toBe(0);
  });

  it("après le verrou : phase R7 (rapport clinique) — usage toujours interdit", () => {
    const st = m18Status(new Date(2026, 11, 2), M0);
    expect(st.pose).toBe(true);
    expect(st.phaseActive).toBe("R7");
  });

  it("jamais de mois écoulés négatifs avant M0", () => {
    const st = m18Status(new Date(2025, 5, 15), M0);
    expect(st.moisEcoules).toBe(0);
    expect(st.pose).toBe(false);
  });
});

describe("libellés réglementaires", () => {
  it("la phrase = bandeau i18n scr.ai_banner (alignement portail/écrans IA)", () => {
    expect(BANNER_TEXT).toBe(
      "Sorties IA NON VALIDÉES cliniquement — investigation R6-R8 en cours, verrou M+18 ; toute décision clinique sur ces sorties est interdite.",
    );
  });

  it("compte à rebours avant le verrou", () => {
    const label = countdownLabel(m18Status(new Date(2026, 8, 15), M0));
    expect(label).toContain("Phase active R6");
    expect(label).toContain("1 décembre 2026");
    expect(label).toContain("dans 77 j");
  });

  it("compte à rebours après le verrou (R7, CE requis)", () => {
    const label = countdownLabel(m18Status(new Date(2027, 0, 10), M0));
    expect(label).toContain("posé");
    expect(label).toContain("R7");
    expect(label).toContain("marquage CE");
  });

  it("tampon par-sortie présent", () => {
    expect(OUTPUT_STAMP).toContain("non décisionnelle");
  });
});

describe("tampon API", () => {
  it("un tampon d'investigation est reconnu", () => {
    expect(
      stampIsInvestigational({
        statut: "investigation",
        protocole: "MEDISUITE-CI-01",
        phases_en_cours: ["R6", "R7", "R8"],
        verrou: "M+18",
        decision_clinique: "interdite",
        avis: BANNER_TEXT,
      }),
    ).toBe(true);
  });

  it("absent, certifié ou muté → non conforme au régime attendu", () => {
    expect(stampIsInvestigational(null)).toBe(false);
    expect(stampIsInvestigational(undefined)).toBe(false);
    expect(
      stampIsInvestigational({
        statut: "certified",
        protocole: "MEDISUITE-CI-01",
        phases_en_cours: [],
        verrou: "M+18",
        decision_clinique: "autorisée",
        avis: "",
      }),
    ).toBe(false);
  });
});
