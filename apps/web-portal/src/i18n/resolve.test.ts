/** Tests i18n — parité des langues, repli fail-soft, RTL, surface complète. */
import { describe, expect, it } from "vitest";
import {
  createT,
  dirFor,
  isLang,
  LANGS,
  storageKeyOf,
} from "./resolve";
import translations from "./translations.json";

describe("i18n resolve (pur)", () => {
  it("parité des clés entre les 4 langues", () => {
    const frKeys = Object.keys(translations.fr).sort();
    for (const lang of ["en", "ar", "es"] as const) {
      expect(Object.keys(translations[lang]).sort(), lang).toEqual(frKeys);
    }
  });

  it("87 clés × 4 langues (nav + 24 modules + écrans fins v0.14 + écrans v0.15)", () => {
    expect(Object.keys(translations.fr)).toHaveLength(87);
    for (const lang of LANGS) {
      expect(Object.keys(translations[lang])).toHaveLength(87);
    }
  });

  it("t() traduit réellement dans chaque langue (pas de clé brute)", () => {
    for (const lang of LANGS) {
      const t = createT(lang);
      expect(t("dashboard").length).toBeGreaterThan(0);
      expect(t("dashboard")).not.toBe("dashboard");
      expect(t("mod.cardiology")).not.toBe("mod.cardiology");
    }
  });

  it("chaque valeur non vide dans les 4 langues", () => {
    for (const lang of LANGS) {
      const t = createT(lang);
      for (const key of Object.keys(translations.fr)) {
        expect((t(key as never) ?? "").trim().length, `${lang}:${key}`)
          .toBeGreaterThan(0);
      }
    }
  });

  it("dirFor : arabe RTL, autres LTR", () => {
    expect(dirFor("ar")).toBe("rtl");
    for (const lang of ["fr", "en", "es"] as const) {
      expect(dirFor(lang)).toBe("ltr");
    }
  });

  it("langue stockée invalide → fr (fail-soft, jamais d'écran vide)", () => {
    expect(storageKeyOf("zh")).toBe("fr");
    expect(storageKeyOf(null)).toBe("fr");
    expect(isLang("es")).toBe(true);
    expect(isLang("de")).toBe(false);
  });
});
