/** TropiRAG — logique pure de l'aide à la décision clinique (testée sans React).
 *
 *  Pont avec l'API TropiRAG (services/tropirag-service, port 8304) :
 *  POST /api/v1/cases analyse un cas fièvre + voyage selon 170 règles
 *  déterministes + RAG sur 47 unités de preuve OMS/CDC/MSF. L'IA est
 *  encadrée : le safety gate et le rule engine restent l'autorité clinique
 *  (IA ≠ autorité clinique). */

export interface TrSymptom { code: string; fr: string; en?: string }

/** Repli si la taxonomy backend est indisponible (offline-first). */
export const SYMPTOM_FALLBACK: TrSymptom[] = [
  { code: "fever", fr: "fièvre" },
  { code: "high_fever", fr: "fièvre élevée" },
  { code: "headache", fr: "céphalées" },
  { code: "chills", fr: "frissons" },
  { code: "myalgia", fr: "myalgies" },
  { code: "arthralgia", fr: "arthralgies" },
  { code: "vomiting", fr: "vomissements" },
  { code: "nausea", fr: "nausées" },
  { code: "diarrhea", fr: "diarrhée" },
  { code: "abdominal_pain", fr: "douleurs abdominales" },
  { code: "jaundice", fr: "ictère" },
  { code: "cough", fr: "toux" },
  { code: "dyspnea", fr: "dyspnée" },
  { code: "chest_pain", fr: "douleur thoracique" },
  { code: "rash", fr: "éruption cutanée" },
  { code: "conjunctival_injection", fr: "injection conjonctivale" },
  { code: "dark_urine", fr: "urines foncées" },
  { code: "fatigue", fr: "fatigue" },
  { code: "confusion", fr: "confusion" },
  { code: "convulsions", fr: "convulsions" },
  { code: "coma", fr: "coma" },
  { code: "prostration", fr: "prostration" },
  { code: "bleeding_gums", fr: "saignements gingivaux" },
  { code: "abnormal_bleeding", fr: "saignements anormaux" },
  { code: "neck_stiffness", fr: "raideur de nuque" },
  { code: "bone_pain", fr: "douleurs osseuses" },
];

export const TR_COUNTRIES: Array<{ code: string; label: string }> = [
  { code: "CI", label: "Côte d'Ivoire" },
  { code: "GH", label: "Ghana" },
  { code: "BF", label: "Burkina Faso" },
  { code: "ML", label: "Mali" },
  { code: "SN", label: "Sénégal" },
  { code: "GN", label: "Guinée" },
  { code: "TG", label: "Togo" },
  { code: "BJ", label: "Bénin" },
  { code: "NG", label: "Nigéria" },
  { code: "LR", label: "Liberia" },
  { code: "SL", label: "Sierra Leone" },
];

export interface TrForm {
  age: number;
  sex: "male" | "female" | "unknown";
  pregnant: "not_applicable" | "pregnant" | "possibly_pregnant" | "not_pregnant";
  temperatureC: number | null;
  symptoms: string[];
  country: string;
  rural: boolean;
  forest: boolean;
  stagnantWater: boolean;
  daysBack: number | null;
  rdtMalaria: "" | "positif" | "negatif";
  freeText: string;
}

export const TR_FORM_DEFAULT: TrForm = {
  age: 25, sex: "female", pregnant: "not_applicable", temperatureC: null,
  symptoms: [], country: "CI", rural: false, forest: false,
  stagnantWater: false, daysBack: null, rdtMalaria: "", freeText: "",
};

export interface TrCaseResult {
  case_id?: string;
  urgency: string;
  severity: string;
  red_flags?: Array<Record<string, unknown>>;
  escalations?: Array<Record<string, unknown>>;
  differentials?: Array<{ disease?: string; probability?: number } & Record<string, unknown>>;
  required_tests?: Array<{ test?: string } & Record<string, unknown>>;
  drug_constraints?: Array<Record<string, unknown>>;
  citations?: Array<{ marker?: string; unit_id?: string; full?: string; quote?: string }>;
  narrative?: string;
  refusal?: string | null;
  disclaimer?: string;
  ai_synthesis?: string | null;   // synthèse IA du mesh (auditée par le Safety Gate)
  ai_layer?: string;              // "deterministic" | "ai-validated"
}

/** État du mesh LLM local (GET /api/v1/inference/nodes). */
export interface TrMesh {
  mode: string;            // deterministic | ollama | vllm
  nodeUp: boolean;         // au moins un nœud joignable
  nodeCount: number;
  version?: string;
}

/** Réduit le rapport /inference/nodes en état exploitable par l'UI. */
export function meshFromNodesReport(rep: {
  inference_mode?: string;
  nodes?: Record<string, { reachable?: boolean; version?: string; models?: number; latency_ms?: number }>;
}): TrMesh {
  const nodes = Object.entries(rep.nodes ?? {});
  const up = nodes.filter(([, v]) => v.reachable);
  return {
    mode: rep.inference_mode ?? "deterministic",
    nodeUp: up.length > 0,
    nodeCount: nodes.length,
    version: up[0]?.[1].version,
  };
}

/** Libellé du badge mesh (affichage + tests). */
export function meshBadgeLabel(m: TrMesh | null): string {
  if (!m) return "mesh : ?";
  if (m.mode !== "deterministic" && m.nodeUp) {
    return `Mesh LLM local actif (${m.nodeCount} nœud${m.nodeCount > 1 ? "s" : ""})`;
  }
  if (m.mode !== "deterministic") return "Mesh LLM configuré — nœud injoignable (repli déterministe)";
  return "IA déterministe hors-ligne";
}

/** Construit le payload POST /api/v1/cases depuis le formulaire.
 *  useAi : demande la synthèse IA du mesh local (le Safety Gate reste
 *  l'autorité finale — refus possible, repli déterministe assuré). */
export function buildCasePayload(f: TrForm, useAi = false): Record<string, unknown> {
  const vitals: Record<string, number> = {};
  if (f.temperatureC !== null && !Number.isNaN(f.temperatureC)) vitals.temperature_c = f.temperatureC;
  const travel: Record<string, unknown> = {
    segments: [{
      country: f.country, rural_stay: f.rural,
      forest_stay: f.forest, stagnant_water: f.stagnantWater,
    }],
  };
  if (f.daysBack !== null && !Number.isNaN(f.daysBack)) travel.days_back = f.daysBack;
  const labResults: Array<Record<string, string>> = [];
  if (f.rdtMalaria) labResults.push({ test: "rdt_malaria", value: f.rdtMalaria });
  return {
    patient: { age: f.age, sex: f.sex, pregnant: f.pregnant },
    symptoms: f.symptoms.map((code) => ({ code })),
    symptom_codes: [...f.symptoms],
    vitals: Object.keys(vitals).length ? vitals : null,
    travel,
    lab_results: labResults,
    free_text: f.freeText || null,
    use_ai: useAi,
    language: "fr",
  };
}

/** Libellés FR des niveaux d'urgence TropiRAG (échelle OMS-simplifiée). */
export const URGENCY_LABEL: Record<string, string> = {
  routine: "Routine", priority: "Prioritaire",
  emergency: "Urgence", immediate: "Danger vital immédiat",
};

export const SEVERITY_LABEL: Record<string, string> = {
  none: "non évaluée", mild: "légère", moderate: "modérée", severe: "sévère",
};

/** Classe CSS du badge d'urgence (styles.css). */
export function urgencyClass(urgency: string): string {
  if (urgency === "immediate") return "critical";
  if (urgency === "emergency") return "critical";
  if (urgency === "priority") return "warn";
  return "ok";
}

/** Déduplique les tests requis (le rule engine peut répéter un examen). */
export function dedupeTests(
  tests: Array<{ test?: string } & Record<string, unknown>> | undefined,
): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const t of tests ?? []) {
    const code = (t.test ?? "").trim();
    if (code && !seen.has(code)) { seen.add(code); out.push(code); }
  }
  return out;
}

/** Extrait un libellé lisible d'un red flag / contrainte (clés variables). */
export function pickLabel(obj: Record<string, unknown> | undefined, fallbackKeys: string[]): string {
  if (!obj) return "";
  for (const k of ["label", "reason", "description", "message", "constraint", "drug", ...fallbackKeys]) {
    const v = obj[k];
    if (typeof v === "string" && v.trim()) return v;
    if (typeof v === "number") return String(v);
  }
  for (const v of Object.values(obj)) {
    if (typeof v === "string" && v.trim() && v.length < 160) return v;
  }
  return JSON.stringify(obj);
}
