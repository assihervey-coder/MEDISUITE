/** Générateur PDF minimal — impression de la fiche patient (good-to-have).
 *  Zéro dépendance, offline-first (docs/OFFLINE-PORTAL.md) : PDF 1.4 avec
 *  polices standard Helvetica (WinAnsiEncoding → français intégral), streams
 *  bruts non compressés (lisibles/testables), A4 multi-pages.
 *
 *  Le contenu clinique reste exactement celui affiché à l'écran : identité,
 *  consentements RGPD/loi CI n°2013-450, encounters, diagnostics CIM-10. */

// ————————————————————————————— encodage WinAnsi (CP1252)

/** Caractères hors Latin-1 présents en WinAnsi (et l'inverse n'existe pas). */
const WINANSI_MAP: Record<string, string> = {
  "\u20AC": "\u0080", "\u201A": "\u0082", "\u0192": "\u0083", "\u201E": "\u0084",
  "\u2026": "\u0085", "\u2020": "\u0086", "\u2021": "\u0087", "\u02C6": "\u0088",
  "\u2030": "\u0089", "\u0160": "\u008A", "\u2039": "\u008B", "\u0152": "\u008C",
  "\u017D": "\u008E", "\u2018": "\u0091", "\u2019": "\u0092", "\u201C": "\u0093",
  "\u201D": "\u0094", "\u2022": "\u0095", "\u2013": "\u0096", "\u2014": "\u0097",
  "\u02DC": "\u0098", "\u2122": "\u0099", "\u0161": "\u009A", "\u203A": "\u009B",
  "\u0153": "\u009C", "\u017E": "\u009E", "\u0178": "\u009F",
};

/** Normalise (NFC) puis ramène chaque caractère à UN code ≤ 0xFF (1 octet). */
export function toWinAnsi(input: string): string {
  const s = input.normalize("NFC");
  let out = "";
  for (const ch of s) {
    const mapped = WINANSI_MAP[ch];
    if (mapped !== undefined) out += mapped;
    else if (ch.charCodeAt(0) <= 0xff) out += ch;
    else out += "?";
  }
  return out;
}

/** Échappement d'une chaîne littérale PDF (parenthèses, anti-slash, contrôles). */
function pdfEscape(s: string): string {
  return s.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)")
    .replace(/[\x00-\x1f]/g, (c) => "\\" + c.charCodeAt(0).toString(8).padStart(3, "0"));
}

// ————————————————————————————— métriques Helvetica approchées
// Classes de largeur (unités /1000) suffisantes pour tronquer les cellules.

function charWidthUnit(ch: string): number {
  if (ch === " ") return 278;
  if ("iIl1jft.,:;'`|!(){}[]/-r".includes(ch)) return 315;
  if ("mMWw@%".includes(ch)) return 850;
  if (/[0-9]/.test(ch)) return 556;
  if (ch >= "A" && ch <= "Z") return 690;
  if (ch >= "a" && ch <= "z") return 545;
  return 556;
}

export function textWidth(s: string, size: number, bold = false): number {
  let u = 0;
  for (const ch of toWinAnsi(s)) u += charWidthUnit(ch);
  return (u / 1000) * size * (bold ? 1.08 : 1);
}

/** Tronque au besoin avec "…" pour tenir dans maxW points. */
function fitText(s: string, size: number, maxW: number, bold = false): string {
  if (textWidth(s, size, bold) <= maxW) return s;
  let t = s;
  while (t.length > 1 && textWidth(t + "…", size, bold) > maxW) t = t.slice(0, -1);
  return t + "…";
}

// ————————————————————————————— primitives de dessin

type RGB = [number, number, number];
const INK: RGB = [0.1, 0.125, 0.173];
const MUTED: RGB = [0.39, 0.46, 0.55];
const PRIMARY: RGB = [0.059, 0.298, 0.506];
const LINE: RGB = [0.84, 0.87, 0.91];
const ZEBRA: RGB = [0.957, 0.969, 0.98];
const OK: RGB = [0.082, 0.498, 0.239];
const WARN: RGB = [0.706, 0.325, 0.035];

const n2 = (v: number) => (Math.round(v * 100) / 100).toString();

class Page {
  ops = "";
  y = A4_H - M; // curseur courant (haut → bas)

  text(x: number, y: number, s: string, o: {
    size?: number; bold?: boolean; italic?: boolean; color?: RGB; align?: "left" | "right";
  } = {}): void {
    const size = o.size ?? 9;
    const font = o.bold ? "/F2" : o.italic ? "/F3" : "/F1";
    let tx = x;
    if (o.align === "right") tx = x - textWidth(s, size, !!o.bold);
    const c = o.color ?? INK;
    this.ops += `q ${c[0]} ${c[1]} ${c[2]} rg BT ${font} ${size} Tf `
      + `1 0 0 1 ${n2(tx)} ${n2(y)} Tm (${pdfEscape(toWinAnsi(s))}) Tj ET Q\n`;
  }

  rect(x: number, y: number, w: number, h: number, fill: RGB): void {
    this.ops += `q ${fill[0]} ${fill[1]} ${fill[2]} rg ${n2(x)} ${n2(y)} ${n2(w)} ${n2(h)} re f Q\n`;
  }

  line(x1: number, y1: number, x2: number, y2: number, color = LINE, w = 0.7): void {
    this.ops += `q ${color[0]} ${color[1]} ${color[2]} RG ${w} w ${n2(x1)} ${n2(y1)} m ${n2(x2)} ${n2(y2)} l S Q\n`;
  }

  circle(cx: number, cy: number, r: number, fill: RGB): void {
    const k = r * 0.5523, c = `${fill[0]} ${fill[1]} ${fill[2]} rg`;
    this.ops += `q ${c} ${n2(cx)} ${n2(cy + r)} m `
      + `${n2(cx + k)} ${n2(cy + r)} ${n2(cx + r)} ${n2(cy + k)} ${n2(cx + r)} ${n2(cy)} c `
      + `${n2(cx + r)} ${n2(cy - k)} ${n2(cx + k)} ${n2(cy - r)} ${n2(cx)} ${n2(cy - r)} c `
      + `${n2(cx - k)} ${n2(cy - r)} ${n2(cx - r)} ${n2(cy - k)} ${n2(cx - r)} ${n2(cy)} c `
      + `${n2(cx - r)} ${n2(cy + k)} ${n2(cx - k)} ${n2(cy + r)} ${n2(cx)} ${n2(cy + r)} c f Q\n`;
  }
}

const A4_W = 595, A4_H = 842, M = 46;
const CONTENT_W = A4_W - 2 * M; // 503 pt

// ————————————————————————————— fiche patient

export interface PdfPatient {
  numero_dossier: string; nom: string; prenoms: string; sexe: string;
  date_naissance: string; age: number; telephone?: string; ville?: string;
  commune?: string; cnam?: string; groupe_sanguin?: string; consent_ia: boolean;
  consent_recherche?: boolean; pseudonyme: string;
}
export interface PdfEncounter { date: string; motif: string; classe: string; service?: string; prescripteur?: string }
export interface PdfCondition { cim10: string; libelle: string; severite?: string; statut: string }
export interface PdfMeta { generePar?: string; role?: string }

const dateFr = (iso: string): string => {
  const d = new Date(iso);
  return isNaN(d.getTime()) ? iso : d.toLocaleDateString("fr-FR");
};

export function buildPatientPdf(
  p: PdfPatient, encounters: PdfEncounter[], conditions: PdfCondition[], meta: PdfMeta = {},
): Uint8Array {
  const pages: Page[] = [];
  const now = new Date();
  const editDate = now.toLocaleDateString("fr-FR");
  const editTime = now.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  const fullName = `${p.nom} ${p.prenoms}`.trim();
  const headerNext = (pg: Page): void => {
    pg.text(M, A4_H - 34, `Fiche patient — ${fitText(fullName, 9, 330, true)} (${p.numero_dossier})`,
      { size: 9, bold: true, color: PRIMARY });
    pg.line(M, A4_H - 44, A4_W - M, A4_H - 44);
    pg.y = A4_H - 64;
  };

  // — page 1 : bandeau
  const pg1 = new Page();
  pages.push(pg1);
  pg1.y = A4_H - M - 58;
  pg1.rect(M, pg1.y, CONTENT_W, 58, PRIMARY);
  pg1.text(M + 14, pg1.y + 36, "MEDISUITE", { size: 17, bold: true, color: [1, 1, 1] });
  pg1.text(M + 14, pg1.y + 17, "Portail Clinique — fiche patient", { size: 8.5, color: [0.78, 0.87, 0.95] });
  pg1.text(A4_W - M - 12, pg1.y + 36, "FICHE PATIENT", { size: 10, bold: true, color: [1, 1, 1], align: "right" });
  pg1.text(A4_W - M - 12, pg1.y + 17, `éditée le ${editDate} à ${editTime}`, { size: 8, color: [0.78, 0.87, 0.95], align: "right" });
  pg1.y -= 26;

  // — identité
  pg1.text(M, pg1.y, fullName, { size: 16, bold: true });
  pg1.text(M + textWidth(fullName, 16, true) + 10, pg1.y, `${p.sexe} · ${p.age} ans`, { size: 10, color: MUTED });
  pg1.y -= 15;
  pg1.text(M, pg1.y, `Dossier ${p.numero_dossier}`, { size: 9, color: MUTED });
  pg1.y -= 14;
  pg1.line(M, pg1.y, A4_W - M, pg1.y);
  pg1.y -= 20;

  const col2 = A4_W / 2 + 30;
  const kv = (x: number, label: string, value: string): void => {
    pg1.text(x, pg1.y, label.toUpperCase(), { size: 7.5, color: MUTED });
    pg1.text(x, pg1.y - 13, fitText(value || "—", 9.5, CONTENT_W / 2 - 40), { size: 9.5 });
  };
  const rows: Array<[string, string, string, string]> = [
    ["N° dossier", p.numero_dossier, "Naissance", `${dateFr(p.date_naissance)} (${p.age} ans)`],
    ["Téléphone", p.telephone ?? "", "Commune / Ville", [p.commune, p.ville].filter(Boolean).join(" · ")],
    ["Groupe sanguin", p.groupe_sanguin ?? "", "CNAM", p.cnam ?? ""],
    ["Pseudonyme recherche", p.pseudonyme.slice(0, 24) + "…", "Établi par", meta.generePar ? `${meta.generePar}${meta.role ? ` (${meta.role})` : ""}` : ""],
  ];
  for (const [l1, v1, l2, v2] of rows) {
    kv(M, l1, v1);
    kv(col2, l2, v2);
    pg1.y -= 32;
  }

  // — consentements
  pg1.y -= 8;
  sectionTitle(pg1, "Consentements (RGPD / loi CI n°2013-450)");
  const consentLine = (y: number, label: string, ok: boolean): void => {
    pg1.circle(M + 4, y + 2.6, 3.6, ok ? OK : WARN);
    pg1.text(M + 14, y, `${label} — ${ok ? "accordé" : "refusé"}`, { size: 9.5, color: ok ? OK : WARN });
  };
  consentLine(pg1.y, "IA diagnostique", p.consent_ia);
  pg1.y -= 17;
  consentLine(pg1.y, "Recherche clinique", !!p.consent_recherche);
  pg1.y -= 30;

  // — consultations (tableau paginé) — la page courante porte son propre curseur y
  let pg = pages[pages.length - 1];
  pg.y -= 26;
  sectionTitle(pg, `Consultations (${encounters.length})`);
  const encCols: Array<[string, number]> = [["Date", 62], ["Motif", 213], ["Classe", 42], ["Service", 92], ["Prescripteur", 94]];
  drawTableHeader(pg, encCols);
  if (encounters.length === 0) pg.text(M + 6, pg.y - 14, "Aucune consultation enregistrée.", { size: 9, italic: true, color: MUTED });
  for (const e of encounters) {
    if (pg.y - 20 < 60) { pg = new Page(); pages.push(pg); headerNext(pg); drawTableHeader(pg, encCols); }
    pg.rect(M, pg.y - 15.5, CONTENT_W, 17, ZEBRA);
    let x = M + 4;
    pg.text(x, pg.y - 4, fitText(dateFr(e.date), 8.5, 58), { size: 8.5 }); x += 62;
    pg.text(x, pg.y - 4, fitText(e.motif, 8.5, 209), { size: 8.5 }); x += 213;
    pg.text(x, pg.y - 4, e.classe, { size: 8.5, bold: true }); x += 42;
    pg.text(x, pg.y - 4, fitText(e.service || "—", 8.5, 88), { size: 8.5 }); x += 92;
    pg.text(x, pg.y - 4, fitText(e.prescripteur || "—", 8.5, 90), { size: 8.5 });
    pg.y -= 17;
  }

  // — diagnostics CIM-10 (tableau paginé)
  pg.y -= 26;
  if (pg.y - 40 < 60) { pg = new Page(); pages.push(pg); headerNext(pg); }
  sectionTitle(pg, `Diagnostics CIM-10 (${conditions.length})`);
  const cimCols: Array<[string, number]> = [["Code", 68], ["Libellé", 265], ["Sévérité", 78], ["Statut", 92]];
  drawTableHeader(pg, cimCols);
  if (conditions.length === 0) pg.text(M + 6, pg.y - 14, "Aucun diagnostic codé.", { size: 9, italic: true, color: MUTED });
  for (const c of conditions) {
    if (pg.y - 20 < 60) { pg = new Page(); pages.push(pg); headerNext(pg); drawTableHeader(pg, cimCols); }
    pg.rect(M, pg.y - 15.5, CONTENT_W, 17, ZEBRA);
    let x = M + 4;
    pg.text(x, pg.y - 4, c.cim10, { size: 8.5, bold: true }); x += 68;
    pg.text(x, pg.y - 4, fitText(c.libelle, 8.5, 261), { size: 8.5 }); x += 265;
    pg.text(x, pg.y - 4, c.severite || "—", { size: 8.5, color: c.severite === "sévère" ? [0.66, 0.13, 0.14] : INK }); x += 78;
    pg.text(x, pg.y - 4, c.statut, { size: 8.5, color: c.statut === "active" ? WARN : OK });
    pg.y -= 17;
  }

  // — footers (une fois le nombre de pages connu)
  const footerConf = "Document confidentiel — secret médical protégé (loi CI n°2013-450) · MEDISUITE";
  pages.forEach((pg, i) => {
    pg.line(M, 40, A4_W - M, 40);
    pg.text(M, 28, footerConf, { size: 7.5, color: MUTED });
    pg.text(A4_W - M, 28, `Page ${i + 1} / ${pages.length}`, { size: 7.5, color: MUTED, align: "right" });
  });

  return assemble(pages, `Fiche patient — ${fullName}`);
}

function sectionTitle(pg: Page, title: string): void {
  pg.text(M, pg.y, title, { size: 10.5, bold: true, color: PRIMARY });
  pg.line(M, pg.y - 5, A4_W - M, pg.y - 5, [0.75, 0.81, 0.88]);
  pg.y -= 22;
}

function drawTableHeader(pg: Page, cols: Array<[string, number]>): void {
  pg.rect(M, pg.y - 13, CONTENT_W, 15, [0.239, 0.302, 0.38]);
  let x = M + 4;
  for (const [label, w] of cols) {
    pg.text(x, pg.y - 4, label, { size: 8, bold: true, color: [1, 1, 1] });
    x += w;
  }
  pg.y -= 15.5;
}

// ————————————————————————————— assemblage du fichier PDF

function bytesOf(s: string): Uint8Array {
  const out = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i) & 0xff;
  return out;
}

function concat(chunks: Uint8Array[]): Uint8Array {
  const total = chunks.reduce((a, c) => a + c.length, 0);
  const out = new Uint8Array(total);
  let o = 0;
  for (const c of chunks) { out.set(c, o); o += c.length; }
  return out;
}

function assemble(pages: Page[], title: string): Uint8Array {
  const nPages = pages.length;
  const objs: string[] = [];
  // 1 Catalog · 2 Pages · 3 Info · 4-6 Fonts · puis Page/Content par page
  objs.push("<< /Type /Catalog /Pages 2 0 R >>");
  const kids = pages.map((_, i) => `${7 + 2 * i} 0 R`).join(" ");
  objs.push(`<< /Type /Pages /Kids [${kids}] /Count ${nPages} >>`);
  objs.push(`<< /Title (${pdfEscape(toWinAnsi(title))}) /Author (MEDISUITE) `
    + `/Creator (MEDISUITE Portal) /Producer (MEDISUITE pdf-lite) >>`);
  objs.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>");
  objs.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>");
  objs.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>");
  pages.forEach((pg, i) => {
    objs.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${A4_W} ${A4_H}] `
      + `/Resources << /Font << /F1 4 0 R /F2 5 0 R /F3 6 0 R >> >> /Contents ${8 + 2 * i} 0 R >>`);
    objs.push(`<< /Length ${bytesOf(pg.ops).length} >>\nstream\n${pg.ops}endstream`);
  });

  const chunks: Uint8Array[] = [];
  let pos = 0;
  const offsets: number[] = [];
  const push = (s: string): void => { chunks.push(bytesOf(s)); pos += bytesOf(s).length; };

  push("%PDF-1.4\n%\u00E2\u00E3\u00CF\u00D3\n");
  objs.forEach((body, i) => {
    offsets.push(pos);
    push(`${i + 1} 0 obj\n${body}\nendobj\n`);
  });
  const xrefPos = pos;
  const xref = `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n`
    + offsets.map((o) => `${String(o).padStart(10, "0")} 00000 n \n`).join("");
  push(xref);
  push(`trailer\n<< /Size ${objs.length + 1} /Root 1 0 R /Info 3 0 R >>\nstartxref\n${xrefPos}\n%%EOF\n`);
  return concat(chunks);
}
