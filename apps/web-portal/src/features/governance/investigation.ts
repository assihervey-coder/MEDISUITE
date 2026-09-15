/**
 * Gouvernance clinique — investigation MEDISUITE-CI-01, verrou M+18 (v0.14).
 *
 * Miroir frontend du module backend `tropirag.governance.investigation` :
 * UN libellé réglementaire (identique à la clé i18n `scr.ai_banner`, déjà
 * affichée sur les 28 écrans AiAssist) et UN calendrier M+ pour le compte à
 * rebours du verrou de base. Logique pure, sans réseau ni store — le
 * composant GovernanceBanner ne fait que l'affichage.
 *
 * Phases (plan de validation v1.0.0) : R6 inclusions+monitoring → VERROU DE
 * BASE M+18 → R7 rapport clinique (MEDDEV 2.7/1) → R8 notifié + marquage CE.
 * Tant que l'investigation est ouverte, toute décision clinique fondée sur
 * une sortie IA est interdite — l'interdiction est aussi appliquée côté API
 * (tampon `governance` + garde 451 sur POST /api/v1/decision/finalize).
 */

export const PROTOCOL = "MEDISUITE-CI-01";

/** Phases d'investigation restantes avant usage décisionnel. */
export const PHASES_IN_PROGRESS = ["R6", "R7", "R8"] as const;

export const LOCK_LABEL = "M+18";

/** Phrase réglementaire — doit rester identique à `scr.ai_banner` (i18n). */
export const BANNER_TEXT =
  "Sorties IA NON VALIDÉES cliniquement — investigation R6-R8 en cours, verrou M+18 ; toute décision clinique sur ces sorties est interdite.";

/** Tampon apposé sur CHAQUE sortie IA restituée (résultats, synthèses). */
export const OUTPUT_STAMP = "Sortie d'investigation — non décisionnelle";

/** Jalon de déploiement de l'investigation (M0) — aligné sur le backend
 * (tropirag.governance.investigation.default_m0, surcharge M0 côté serveur). */
export const M0: Readonly<Date> = new Date(2025, 5, 1); // 2025-06-01

/** Décalage calendaire en mois pleins (clamp fin de mois : 31/02 → 28/02). */
export function addMonths(d: Date, months: number): Date {
  const y = d.getFullYear() + Math.floor((d.getMonth() + months) / 12);
  const m = (d.getMonth() + months) % 12;
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  return new Date(y, m, Math.min(d.getDate(), daysInMonth));
}

/** Date du verrou de base M+18 (clôture R6 — inclusions + monitoring). */
export function m18Date(m0: Readonly<Date> = M0): Date {
  return addMonths(new Date(m0), 18);
}

const DAY_MS = 86_400_000;

function startOfDay(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

/** Différence en jours pleins (a − b). */
export function daysBetween(a: Readonly<Date>, b: Readonly<Date>): number {
  return Math.round((startOfDay(new Date(a)).getTime() - startOfDay(new Date(b)).getTime()) / DAY_MS);
}

export interface M18Status {
  /** Verrou de base posé (date atteinte). */
  pose: boolean;
  /** Phase dérivée — verrou non posé → R6 ; posé → R7 ; R8 = décision
   * humaine (notifié), non dérivable (cf. features/study/status-logic.ts). */
  phaseActive: "R6" | "R7";
  /** Date ISO du verrou M+18. */
  verrouIso: string;
  /** Jours restants avant M+18 (0 si posé). */
  joursAvantVerrou: number;
  /** Mois pleins écoulés depuis M0. */
  moisEcoules: number;
}

/** État du verrou M+18 pour `today` — réplique `m18_status` backend. */
export function m18Status(today: Readonly<Date> = new Date(), m0: Readonly<Date> = M0): M18Status {
  const m18 = m18Date(m0);
  const pose = startOfDay(new Date(today)).getTime() >= startOfDay(new Date(m18)).getTime();
  const moisEcoules =
    (today.getFullYear() - m0.getFullYear()) * 12 + (today.getMonth() - m0.getMonth()) -
    (today.getDate() < m0.getDate() ? 1 : 0);
  return {
    pose,
    phaseActive: pose ? "R7" : "R6",
    verrouIso: m18.toISOString().slice(0, 10),
    joursAvantVerrou: Math.max(0, daysBetween(m18, today)),
    moisEcoules: Math.max(0, moisEcoules),
  };
}

/** Ligne de compte à rebours du bandeau (fr, cohérente avec le portail). */
export function countdownLabel(st: M18Status = m18Status()): string {
  const dateFr = new Date(st.verrouIso + "T00:00:00").toLocaleDateString("fr-FR", {
    day: "numeric", month: "long", year: "numeric",
  });
  return st.pose
    ? `Verrou de base M+18 posé (${dateFr}) — phase active ${st.phaseActive} ; usage décisionnel toujours interdit jusqu'au marquage CE.`
    : `Phase active ${st.phaseActive} · verrou de base M+18 : ${dateFr} (dans ${st.joursAvantVerrou} j)`;
}

/** Bloc `governance` renvoyé par l'API TropiRAG (tampon des sorties CDS). */
export interface GovernanceStamp {
  statut: "investigation" | "certified";
  protocole: string;
  phases_en_cours: string[];
  verrou: string;
  decision_clinique: "interdite" | "autorisée";
  avis: string;
}

/** Le tampon reçu d'une sortie CDS est-il conforme au régime attendu ? */
export function stampIsInvestigational(st: GovernanceStamp | undefined | null): boolean {
  return !!st && st.statut === "investigation" && st.decision_clinique === "interdite";
}
