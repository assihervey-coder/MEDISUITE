/** Tests de la logique pure de l'écran promoteur study status/lock (v0.9). */
import { describe, expect, it } from "vitest";
import {
  activePhase,
  formatChecksum,
  lockPayload,
  lockReadiness,
  siteLabel,
  TIMELINE,
} from "./status-logic";

const OK = { locked: false, sujets: 12, entrees_signees: 40, requetes_ouvertes: 0 };

describe("TIMELINE", () => {
  it("couvre R5→R8 avec les fenêtres du plan v1.0.0", () => {
    expect(TIMELINE.map((s) => s.jalon)).toEqual(["R5", "R6", "R7", "R8"]);
    const r6 = TIMELINE.find((s) => s.jalon === "R6")!;
    expect(r6.from).toBe(6);
    expect(r6.to).toBe(18); // le verrou M+18 clôture R6
    const r7 = TIMELINE.find((s) => s.jalon === "R7")!;
    expect(r7.detail).toContain("MEDDEV 2.7/1");
  });
});

describe("activePhase", () => {
  it("R6 tant que la base n'est pas verrouillée", () => {
    expect(activePhase(OK)).toBe("R6");
  });
  it("R7 dès que le verrou M+18 est posé", () => {
    expect(activePhase({ ...OK, locked: true })).toBe("R7");
  });
});

describe("lockReadiness", () => {
  it("prêt quand zéro requête ouverte et données signées", () => {
    expect(lockReadiness(OK)).toEqual({ ready: true, blocages: [] });
  });
  it("bloqué par des requêtes SDV ouvertes (plan-monitoring §5)", () => {
    const r = lockReadiness({ ...OK, requetes_ouvertes: 3 });
    expect(r.ready).toBe(false);
    expect(r.blocages[0]).toContain("3 requête(s)");
  });
  it("bloqué sur base vide", () => {
    const r = lockReadiness({ ...OK, sujets: 0 });
    expect(r.ready).toBe(false);
    expect(r.blocages[0]).toContain("base vide");
  });
  it("bloqué si sujets présents mais aucune entrée signée", () => {
    const r = lockReadiness({ ...OK, entrees_signees: 0 });
    expect(r.ready).toBe(false);
    expect(r.blocages[0]).toContain("aucune entrée signée");
  });
});

describe("formatChecksum", () => {
  it("retourne — pour un checksum absent", () => {
    expect(formatChecksum(undefined)).toBe("—");
    expect(formatChecksum("")).toBe("—");
  });
  it("laisse tel quel un checksum court", () => {
    expect(formatChecksum("abc123")).toBe("abc123");
  });
  it("compacte un SHA-256 (8 premiers + … + 8 derniers)", () => {
    const sha = "a".repeat(64);
    expect(formatChecksum(sha)).toBe("aaaaaaaa…aaaaaaaa");
    expect(formatChecksum(sha)).toHaveLength(17);
  });
});

describe("lockPayload", () => {
  const base = { temoin1: "Kouassi A.", temoin2: "Traoré F.", declaration: "ok", confirmation: "" };

  it("rejette une confirmation incorrecte", () => {
    const r = lockPayload({ ...base, confirmation: "verrou" }, "MEDISUITE-CI-01");
    expect(r.ok).toBe(false);
    expect(r.errors[0]).toContain("VERROU MEDISUITE-CI-01");
  });
  it("accepte le payload exact avec la phrase de confirmation", () => {
    const r = lockPayload(
      { ...base, confirmation: "VERROU MEDISUITE-CI-01" },
      "MEDISUITE-CI-01",
    );
    expect(r.ok).toBe(true);
    expect(r.body).toEqual({
      temoins: ["Kouassi A.", "Traoré F."],
      declaration: "ok",
    });
  });
  it("exige deux témoins distincts (insensible à la casse)", () => {
    const r1 = lockPayload(
      { ...base, temoin1: "", temoin2: "x", confirmation: "VERROU MEDISUITE-CI-01" },
      "MEDISUITE-CI-01",
    );
    expect(r1.errors[0]).toContain("témoins sont requis");
    const r2 = lockPayload(
      { ...base, temoin2: "kouassi a.", confirmation: "VERROU MEDISUITE-CI-01" },
      "MEDISUITE-CI-01",
    );
    expect(r2.ok).toBe(false);
    expect(r2.errors[0]).toContain("distinctes");
  });
});

describe("siteLabel", () => {
  it("retombe sur un libellé honnête pour un code inconnu", () => {
    expect(siteLabel({ COC: "CHU de Cocody (coordinateur)" }, "COC")).toContain("Cocody");
    expect(siteLabel(undefined, "XYZ")).toBe("site inconnu (XYZ)");
  });
});
