/** Tests de la logique TropiRAG — payload, badges, déduplication, libellés. */
import { describe, expect, it } from "vitest";
import {
  buildCasePayload, dedupeTests, pickLabel, SEVERITY_LABEL, TR_FORM_DEFAULT,
  urgencyClass, URGENCY_LABEL, type TrForm,
} from "./tropirag";

const form: TrForm = {
  ...TR_FORM_DEFAULT,
  age: 34, sex: "female", pregnant: "pregnant",
  temperatureC: 39.2, symptoms: ["fever", "headache"],
  country: "CI", rural: true, daysBack: 5, rdtMalaria: "positif",
  freeText: "Retour de zone rurale depuis 5 jours",
};

describe("buildCasePayload", () => {
  it("mappe le formulaire vers le schéma CaseRequest TropiRAG", () => {
    const p = buildCasePayload(form) as Record<string, any>;
    expect(p.patient).toEqual({ age: 34, sex: "female", pregnant: "pregnant" });
    expect(p.symptoms).toEqual([{ code: "fever" }, { code: "headache" }]);
    expect(p.symptom_codes).toEqual(["fever", "headache"]);
    expect(p.vitals).toEqual({ temperature_c: 39.2 });
    expect(p.travel.segments[0]).toEqual({
      country: "CI", rural_stay: true, forest_stay: false, stagnant_water: false,
    });
    expect(p.travel.days_back).toBe(5);
    expect(p.lab_results).toEqual([{ test: "rdt_malaria", value: "positif" }]);
    expect(p.use_ai).toBe(false);
    expect(p.language).toBe("fr");
  });

  it("omet la température absente et le TDR non réalisé", () => {
    const p = buildCasePayload({ ...TR_FORM_DEFAULT, temperatureC: null, rdtMalaria: "" }) as Record<string, any>;
    expect(p.vitals).toBeNull();
    expect(p.lab_results).toEqual([]);
  });
});

describe("urgencyClass / labels", () => {
  it("classe les 4 niveaux d'urgence sur les badges existants", () => {
    expect(urgencyClass("immediate")).toBe("critical");
    expect(urgencyClass("emergency")).toBe("critical");
    expect(urgencyClass("priority")).toBe("warn");
    expect(urgencyClass("routine")).toBe("ok");
    expect(URGENCY_LABEL.emergency).toBe("Urgence");
    expect(SEVERITY_LABEL.severe).toBe("sévère");
  });
});

describe("dedupeTests", () => {
  it("déduplique les examens répétés par le rule engine", () => {
    expect(dedupeTests([
      { test: "rdt_malaria" }, { test: "cbc" }, { test: "rdt_malaria" }, { test: "cbc" }, { test: "glycemia" },
    ])).toEqual(["rdt_malaria", "cbc", "glycemia"]);
    expect(dedupeTests(undefined)).toEqual([]);
    expect(dedupeTests([{ test: "" }, { test: "  " }])).toEqual([]);
  });
});

describe("pickLabel", () => {
  it("extrait le libellé le plus utile des red flags / contraintes", () => {
    expect(pickLabel({ label: "Paludisme gestationnel", code: "x" }, [])).toBe("Paludisme gestationnel");
    expect(pickLabel({ rule_id: "mal-sev-001", priority: 92 }, ["rule_id"])).toBe("mal-sev-001");
    expect(pickLabel({ drug: "primaquine", constraint_type: "contraindicated" }, [])).toBe("primaquine");
    expect(pickLabel(undefined, [])).toBe("");
  });
});
