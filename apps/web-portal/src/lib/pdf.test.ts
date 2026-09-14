/// <reference types="node" />
/** Tests du générateur PDF fiche patient — structure fichier + encodage + pagination. */
import { describe, expect, it } from "vitest";
import { buildPatientPdf, textWidth, toWinAnsi, type PdfPatient } from "./pdf";

const patient: PdfPatient = {
  numero_dossier: "P-2026-0042", nom: "Konaté", prenoms: "Awa Céline", sexe: "F",
  date_naissance: "1992-03-14", age: 34, telephone: "+225 07 05 05 05 05",
  commune: "Yopougon", ville: "Abidjan", cnam: "CI-Cnam-8842", groupe_sanguin: "O+",
  consent_ia: true, consent_recherche: false, pseudonyme: "a3f9c2e1b7d4f6a8c0e2b4d6f8a0c2e1",
};

const encounters = [
  { date: "2026-08-02", motif: "Fièvre + céphalées (TDR palu +)", classe: "AMB", service: "Médecine interne", prescripteur: "Dr Kouassi" },
  { date: "2026-08-15", motif: "Contrôle post-traitement", classe: "AMB", service: "Médecine interne", prescripteur: "Dr Kouassi" },
];

const conditions = [
  { cim10: "B50.9", libelle: "Paludisme à P. falciparum", severite: "modérée", statut: "résolue" },
  { cim10: "D64.9", libelle: "Anémie", severite: "légère", statut: "active" },
];

/** Reconstitue une chaîne Latin-1 depuis les octets (streams non compressés). */
const latin1 = (b: Uint8Array): string => Array.from(b, (c) => String.fromCharCode(c)).join("");

describe("toWinAnsi", () => {
  it("mappe les caractères hors Latin-1 vers CP1252", () => {
    expect(toWinAnsi("œ")).toBe(String.fromCharCode(0x9c));
    expect(toWinAnsi("…")).toBe(String.fromCharCode(0x85));
    expect(toWinAnsi("—")).toBe(String.fromCharCode(0x97));
  });
  it("garantit un code ≤ 0xFF par caractère (1 octet)", () => {
    for (const ch of toWinAnsi("École d'Abidjan — œuf €…")) expect(ch.charCodeAt(0)).toBeLessThanOrEqual(0xff);
  });
});

describe("textWidth", () => {
  it("reste dans un ordre de grandeur Helvetica plausible", () => {
    // "W" large ≈ 944/1000 ; "i" étroit ≈ 278/1000
    expect(textWidth("W", 10)).toBeGreaterThan(6.5);
    expect(textWidth("i", 10)).toBeLessThan(4);
    expect(textWidth("W", 10, true)).toBeGreaterThan(textWidth("W", 10));
  });
});

describe("buildPatientPdf", () => {
  it("produit un fichier PDF 1.4 complet (header, catalog, xref, EOF)", () => {
    const pdf = latin1(buildPatientPdf(patient, encounters, conditions, { generePar: "Dr Bakayoko", role: "médecin" }));
    expect(pdf.startsWith("%PDF-1.4")).toBe(true);
    expect(pdf).toContain("/Type /Catalog");
    expect(pdf).toContain("/Type /Pages");
    expect(pdf).toContain("/WinAnsiEncoding");
    expect(pdf.trimEnd().endsWith("%%EOF")).toBe(true);
    expect(pdf).toContain("/MediaBox [0 0 595 842]");
  });

  it("a une table xref dont startxref pointe sur l'offset réel", () => {
    const raw = buildPatientPdf(patient, encounters, conditions);
    const pdf = latin1(raw);
    const m = /startxref\n(\d+)\n%%EOF/.exec(pdf);
    expect(m).not.toBeNull();
    const offset = Number(m![1]);
    expect(pdf.slice(offset, offset + 4)).toBe("xref");
    // chaque entrée d'objet : l'offset annoncé doit tomber sur "N 0 obj"
    const objOffsets = [...pdf.matchAll(/^(\d{10}) 00000 n \n/gm)].map((x) => Number(x[1]));
    expect(objOffsets.length).toBeGreaterThanOrEqual(8);
    for (const [i, o] of objOffsets.entries()) {
      expect(pdf.slice(o).startsWith(`${i + 1} 0 obj`)).toBe(true);
    }
  });

  it("contient le contenu clinique (nom, dossier, CIM-10) en clair WinAnsi", () => {
    const pdf = latin1(buildPatientPdf(patient, encounters, conditions));
    expect(pdf).toContain("Konaté"); // é = 0xE9 → Latin-1 direct
    expect(pdf).toContain("P-2026-0042");
    expect(pdf).toContain("B50.9");
    expect(pdf).toContain("Paludisme");
    expect(pdf).toContain("accordé"); // accents contenus dans le corps
    expect(pdf).toContain("Document confidentiel");
  });

  it("génère la meta 'Établi par' quand fournie", () => {
    const pdf = latin1(buildPatientPdf(patient, [], [], { generePar: "Dr Bakayoko", role: "médecin" }));
    expect(pdf).toContain("Dr Bakayoko");
    expect(pdf).toContain("médecin");
  });

  it("pagine densément : 40 encounters sur un minimum de pages (pas 1 ligne/page)", () => {
    const many = Array.from({ length: 40 }, (_, i) => ({
      date: `2026-01-${String((i % 28) + 1).padStart(2, "0")}`,
      motif: `Consultation de suivi n°${i + 1}`, classe: "AMB", service: "Médecine", prescripteur: "Dr X",
    }));
    const pdf = latin1(buildPatientPdf(patient, many, conditions));
    const count = /\/Count (\d+)/.exec(pdf);
    const n = Number(count![1]);
    expect(n).toBeGreaterThan(1);       // débordement → multi-pages
    expect(n).toBeLessThanOrEqual(3);   // mais dense : ~24 lignes/page, pas 1 ligne/page
    expect(pdf).toContain("Page 2 / "); // header de section répété + footer page 2
    expect(pdf).toContain("n°40");      // dernière ligne bien rendue
  });

  it("reste valide avec fiche vide (0 encounter, 0 diagnostic)", () => {
    const pdf = latin1(buildPatientPdf(patient, [], []));
    expect(pdf.startsWith("%PDF-1.4")).toBe(true);
    expect(pdf).toContain("Aucune consultation enregistrée.");
    expect(pdf).toContain("Aucun diagnostic codé.");
  });
});

/** Snapshot visuel : PDF_SNAPSHOT=1 npm test → logs/fiche-sample.pdf (Read pour contrôle). */
if (process.env.PDF_SNAPSHOT) {
  const { writeFileSync, mkdirSync } = await import("node:fs");
  const { resolve } = await import("node:path");
  it("écrit le snapshot (PDF_SNAPSHOT=1)", () => {
    const dir = resolve(process.cwd(), "../../logs");
    mkdirSync(dir, { recursive: true });
    writeFileSync(resolve(dir, "fiche-sample.pdf"),
      buildPatientPdf(patient, [...encounters, ...Array.from({ length: 22 }, (_, i) => ({
        date: "2026-07-30", motif: `Suivi hebdomadaire ${i + 1} — tension, glycémie, observance`, classe: "AMB",
        service: "Médecine interne", prescripteur: "Dr Kouassi N.",
      }))], conditions, { generePar: "Dr Bakayoko", role: "médecin" }));
  });
}
