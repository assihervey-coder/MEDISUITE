/** Types des écrans fins (v0.14) — consommés par registry.generated.ts,
 *  les 4 gabarits de templates/ et la logique pure de logic.ts.
 *  Les données viennent de tools/generate_screens.py (sources de vérité :
 *  services/registry, clinical-rules, configs IA, datasets/registry). */

export type ScreenKind = "overview" | "cas" | "detail" | "ia";

/** Type d'entrée déduit de l'annotation de la fonction de score. */
export type ParamKind = "number" | "text" | "boolean";

/** Signature d'un endpoint de score (fonction réelle de clinical-rules). */
export interface ScoreSig {
  endpoint: string;
  fn: string;
  params: Array<{ name: string; kind: ParamKind; hasDefault: boolean }>;
}

/** Bloc IA du module — relu des configs ai/multimodal + datasets/registry. */
export interface AiInfo {
  task: string;
  modalities: string[];
  missingPolicy: string;
  sharedTrunk: boolean;
  explainability: string[];
  labelTask: string;
  labelNom: string;
  classes: string[];
  features: Array<{ name: string; lo: number; hi: number }>;
}

/** Un écran fin : identité, route, données de service, scores et IA. */
export interface ScreenDef {
  id: string;
  kind: ScreenKind;
  slug: string;
  urlSlug: string;
  moduleNo: number;
  icon: string;
  label: string;
  service: string;
  route: string;
  servicePath: string;
  scores: string[];
  sigs: ScoreSig[];
  ai: AiInfo;
}

/** Ligne de cas clinique — contrat partagé des 24 services de spécialité. */
export interface CaseRow {
  id: string;
  patient_id?: string;
  patient_nom?: string;
  date?: string;
  titre: string;
  severite?: string;
  statut?: string;
  payload?: unknown;
}
