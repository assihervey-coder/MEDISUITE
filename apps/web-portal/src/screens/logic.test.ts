/** Tests de la logique pure des écrans fins (v0.14) — sans React. */
import { describe, expect, it } from "vitest";
import {
  buildScoreBody,
  computeKpis,
  distinct,
  filterCases,
  isSevere,
  paramInputKind,
  siblingRoute,
} from "./logic";
import type { CaseRow, ScreenDef } from "./types";

const CASES: CaseRow[] = [
  { id: "c1", titre: "Mammographie suspecte", patient_nom: "KOUASSI Aya", statut: "actif", severite: "haute" },
  { id: "c2", titre: "RCP colique", patient_nom: "KONÉ Ibrahim", statut: "actif", severite: "" },
  { id: "c3", titre: "Suivi 6 mois", patient_nom: "TRAORÉ Rokia", statut: "clos", severite: "faible" },
];

describe("filterCases", () => {
  it("filtre par requête (titre/patient, insensible à la casse)", () => {
    expect(filterCases(CASES, "mammo", "", "").map((c) => c.id)).toEqual(["c1"]);
    expect(filterCases(CASES, "kouassi", "", "").map((c) => c.id)).toEqual(["c1"]);
  });
  it("filtre par statut et par sévérité exacts", () => {
    expect(filterCases(CASES, "", "clos", "").map((c) => c.id)).toEqual(["c3"]);
    expect(filterCases(CASES, "", "", "haute").map((c) => c.id)).toEqual(["c1"]);
  });
  it("combine les trois filtres", () => {
    expect(filterCases(CASES, "rcp", "actif", "").map((c) => c.id)).toEqual(["c2"]);
    expect(filterCases(CASES, "rcp", "clos", "")).toEqual([]);
  });
  it("ne filtre rien quand tout est vide", () => {
    expect(filterCases(CASES, "  ", "", "")).toHaveLength(3);
  });
});

describe("computeKpis", () => {
  it("compte total/actifs/clos/sévères sans fabriquer de données", () => {
    expect(computeKpis(CASES)).toEqual({ total: 3, actifs: 2, clos: 1, severe: 1 });
    expect(computeKpis([])).toEqual({ total: 0, actifs: 0, clos: 0, severe: 0 });
  });
});

describe("isSevere", () => {
  it("reconnaît les sévérités critiques fr/en, rejette les autres/absentes", () => {
    expect(isSevere("Haute")).toBe(true);
    expect(isSevere("critique")).toBe(true);
    expect(isSevere("high")).toBe(true);
    expect(isSevere("faible")).toBe(false);
    expect(isSevere(undefined)).toBe(false);
    expect(isSevere("")).toBe(false);
  });
});

describe("distinct", () => {
  it("déduit les valeurs de filtre sans doublon ni vide, triées", () => {
    expect(distinct(CASES, "statut")).toEqual(["actif", "clos"]);
    expect(distinct(CASES, "severite")).toEqual(["faible", "haute"]);
  });
});

describe("paramInputKind + buildScoreBody", () => {
  it("mappe les types d'annotation vers les inputs", () => {
    expect(paramInputKind("number")).toBe("number");
    expect(paramInputKind("text")).toBe("text");
    expect(paramInputKind("boolean")).toBe("checkbox");
  });

  const PARAMS = [
    { name: "age", kind: "number" as const, hasDefault: false },
    { name: "sexe", kind: "text" as const, hasDefault: false },
    { name: "stable", kind: "boolean" as const, hasDefault: true },
  ];

  it("envoie les booléens même à false (significatif) et convertit les nombres", () => {
    const body = buildScoreBody(PARAMS, { age: "67", sexe: "F", stable: false });
    expect(body).toEqual({ age: 67, sexe: "F", stable: false });
  });

  it("omet les champs vides (défaut serveur, sinon 422 explicite)", () => {
    const body = buildScoreBody(PARAMS, { age: "", sexe: "M", stable: true });
    expect(body).toEqual({ sexe: "M", stable: true });
  });
});

describe("siblingRoute", () => {
  const screen = {
    urlSlug: "oncology",
    kind: "overview",
    route: "/module/oncology",
    id: "oncology:overview",
    slug: "oncology",
    moduleNo: 3,
    icon: "🎗️",
    label: "Oncologie",
    service: "oncology-service",
    servicePath: "module/oncology",
    scores: [],
    sigs: [],
    ai: {
      task: "multiclass", modalities: [], missingPolicy: "n/d", sharedTrunk: false,
      explainability: [], labelTask: "multiclass", labelNom: "", classes: [], features: [],
    },
  } as ScreenDef;

  it("dérive les routes sœurs depuis la base du module", () => {
    expect(siblingRoute(screen, "overview")).toBe("/module/oncology");
    expect(siblingRoute(screen, "cas")).toBe("/module/oncology/cas");
    expect(siblingRoute(screen, "ia")).toBe("/module/oncology/ia");
    expect(siblingRoute(screen, "detail")).toBe("/module/oncology/cas");
  });
});
