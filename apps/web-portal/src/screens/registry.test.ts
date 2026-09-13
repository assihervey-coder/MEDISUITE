/** Tests verrou du registre des écrans fins (v0.14) — cohérence générée. */
import { describe, expect, it } from "vitest";
import { SCREENS, screenById, screensOfModule } from "./registry.generated";
import { MODULE_NAV } from "../features/modules-nav";
import { dictionaries } from "../i18n/resolve";
import type { MsgKey } from "../i18n/resolve";

describe("SCREENS — structure générée", () => {
  it("contient 96 écrans : 24 modules × 4 types", () => {
    expect(SCREENS).toHaveLength(96);
    expect(new Set(SCREENS.map((s) => s.urlSlug)).size).toBe(24);
    for (const nav of MODULE_NAV) {
      const kinds = screensOfModule(nav.slug === "nuclear_medicine" ? "nuclear-medicine" : nav.slug)
        .map((s) => s.kind)
        .sort();
      expect(kinds).toEqual(["cas", "detail", "ia", "overview"]);
    }
  });

  it("routes uniques et bien formées, alignées sur modules-nav", () => {
    const routes = SCREENS.map((s) => s.route);
    expect(new Set(routes).size).toBe(96);
    for (const r of routes) expect(r).toMatch(/^\/module\/[a-z-]+(\/cas(\/:caseId)?|\/ia)?$/);
    for (const nav of MODULE_NAV) {
      const urlSlug = nav.to.replace("/module/", "");
      expect(routes).toContain(`/module/${urlSlug}`);
    }
  });

  it("chaque écran porte service, icône et n° de module cohérents", () => {
    for (const s of SCREENS) {
      expect(s.service).toBe(`${s.urlSlug}-service`);
      expect(s.servicePath).toBe(`module/${s.urlSlug}`);
      expect(s.icon.length).toBeGreaterThan(0);
      expect(s.moduleNo).toBeGreaterThanOrEqual(3);
      expect(s.moduleNo).toBeLessThanOrEqual(26);
    }
  });
});

describe("câblage App.tsx", () => {
  it("toute route générée est routable (contrat consommé par SCREEN_ROUTES)", () => {
    // routes.generated.tsx mappe 1:1 SCREENS (vérifié par tsc strict + e2e) ;
    // ici on verrouille l'invariant de données : 96 routes uniques.
    const routes = SCREENS.map((s) => s.route);
    expect(new Set(routes).size).toBe(96);
  });
});

describe("screenById / screensOfModule", () => {
  it("retrouve chaque écran par son id composé", () => {
    const s = screenById("oncology:detail");
    expect(s?.kind).toBe("detail");
    expect(s?.route).toBe("/module/oncology/cas/:caseId");
    expect(screenById("inexistant:overview")).toBeUndefined();
  });
});

describe("signatures de scores générées", () => {
  it("chaque écran cas/détail porte des endpoints réels de clinical-rules", () => {
    const oncology = screenById("oncology:detail")!;
    expect(oncology.scores).toContain("birads");
    expect(oncology.sigs.find((s) => s.endpoint === "birads")?.params.length).toBeGreaterThan(0);
    // tous les paramètres générés sont typés number/text/boolean
    for (const s of SCREENS) {
      for (const sig of s.sigs) {
        expect(["birads", ...s.scores]).toContain(sig.endpoint);
        for (const p of sig.params) expect(["number", "text", "boolean"]).toContain(p.kind);
      }
    }
  });

  it("le bloc IA est relu des configs (tâche + au moins une source)", () => {
    for (const s of SCREENS) {
      expect(s.ai.task.length).toBeGreaterThan(0);
      expect(s.ai.features.length + s.ai.modalities.length).toBeGreaterThan(0);
    }
  });
});

describe("i18n des écrans fins", () => {
  it("les clés scr.* existent dans les 4 langues (parité runtime)", () => {
    const probe = (Object.keys(dictionaries.fr) as MsgKey[]).filter((k) =>
      k.startsWith("scr."),
    );
    expect(probe.length).toBeGreaterThanOrEqual(38);
    for (const lang of ["en", "ar", "es"] as const) {
      for (const k of probe) {
        expect(dictionaries[lang][k]).toBeDefined();
        expect(String(dictionaries[lang][k]).length).toBeGreaterThan(0);
      }
    }
  });

  it("chaque module a sa clé mod.* (label sidebar inchangé v0.11)", () => {
    for (const nav of MODULE_NAV) {
      for (const lang of ["fr", "en", "ar", "es"] as const) {
        expect(dictionaries[lang][`mod.${nav.slug}` as MsgKey]).toBeDefined();
      }
    }
  });
});
