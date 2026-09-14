/** Export CSV universel (good-to-have) — échappement RFC 4180 + BOM UTF-8
 *  pour ouverture directe dans Excel/LibreOffice (virgules, guillemets, CRLF). */

/** Échappe une cellule : guillemets doublés, entourage si séparateur/présent. */
function escapeCell(value: unknown): string {
  const s = value === null || value === undefined ? "" : String(value);
  return /[",;\n\r]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

/** Construit le contenu CSV depuis des objets (clés = colonnes, ordre stable). */
export function toCsv(rows: Array<Record<string, unknown>>, columns?: string[]): string {
  if (rows.length === 0) return "";
  const cols = columns ?? Object.keys(rows[0]);
  const header = cols.map(escapeCell).join(",");
  const lines = rows.map((r) => cols.map((c) => escapeCell(r[c])).join(","));
  return [header, ...lines].join("\r\n");
}

/** Déclenche le téléchargement d'un CSV (BOM UTF-8 pour Excel). */
export function downloadCsv(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/** Télécharge un texte quelconque (JSON FHIR, export eCRF…). */
export function downloadFile(filename: string, content: string, mime = "application/json"): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
