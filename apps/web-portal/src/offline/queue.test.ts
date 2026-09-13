/** Tests des règles pures de la file offline (vitest, v0.7). */
import { describe, expect, it } from "vitest";
import {
  isPermanentRejection,
  newClientKey,
  retryDelayMs,
} from "./rules";

describe("retryDelayMs", () => {
  it("double à chaque tentative puis plafonne à 30 s", () => {
    expect(retryDelayMs(0)).toBe(1_000);
    expect(retryDelayMs(1)).toBe(2_000);
    expect(retryDelayMs(2)).toBe(4_000);
    expect(retryDelayMs(5)).toBe(30_000);
    expect(retryDelayMs(50)).toBe(30_000);
  });

  it("tolère un compteur négatif (ne lève pas)", () => {
    expect(retryDelayMs(-3)).toBe(1_000);
  });
});

describe("isPermanentRejection", () => {
  it("4xx hors 408/429 = rejet définitif", () => {
    expect(isPermanentRejection(422)).toBe(true);
    expect(isPermanentRejection(403)).toBe(true);
    expect(isPermanentRejection(404)).toBe(true);
  });

  it("408/429/5xx et succès = rejouable", () => {
    expect(isPermanentRejection(408)).toBe(false);
    expect(isPermanentRejection(429)).toBe(false);
    expect(isPermanentRejection(502)).toBe(false);
    expect(isPermanentRejection(200)).toBe(false);
  });
});

describe("newClientKey", () => {
  it("produit des clés uniques non vides", () => {
    const a = newClientKey();
    const b = newClientKey();
    expect(a).toBeTruthy();
    expect(b).toBeTruthy();
    expect(a).not.toBe(b);
  });
});
