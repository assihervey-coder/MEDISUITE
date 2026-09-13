/**
 * Logique pure de l'écran promoteur « study status / lock » (v0.9).
 *
 * Tout ce qui est testable est détaché du réseau et du store : la timeline
 * du plan R1-R9 (08-plan-validation-v1.0.0.md), la dérivation de la phase
 * active, la lisibilité du verrou M+18 (plan-monitoring §5 + protocole
 * §8) et la validation du formulaire de lock. Le composant React ne fait
 * que l'affichage et les appels API — même découplage que offline/rules.ts.
 */

export interface TimelineStep {
  jalon: string;
  from: number; // M+ (mois d'ouverture)
  to: number; // M+ (mois de clôture ; 30+ pour R8)
  titre: string;
  detail: string;
}

/** Fenêtres du plan de validation v1.0.0 (R5→R8 — l'investigation et la certification). */
export const TIMELINE: TimelineStep[] = [
  {
    jalon: "R5",
    from: 2,
    to: 6,
    titre: "Protocole + soumissions",
    detail:
      "Protocole MEDISUITE-CI-01, signatures terrain, ANOC-CI, Ministère, PACTR, accords sites",
  },
  {
    jalon: "R6",
    from: 6,
    to: 18,
    titre: "Inclusions + monitoring",
    detail:
      "Inclusions eCRF, visites de monitoring A4, adjudication, sûreté 30 j — se termine par le VERROU DE BASE M+18",
  },
  {
    jalon: "R7",
    from: 18,
    to: 21,
    titre: "Rapport clinique",
    detail:
      "Analyse SAP après extraction data manager → rapport évaluation clinique MEDDEV 2.7/1 rev 4 (ADR-0026), bénéfice-risque final",
  },
  {
    jalon: "R8",
    from: 21,
    to: 31,
    titre: "Notifié + certification",
    detail: "EUDAMED, audit organisme notifié, marquage CE (art. 52-54)",
  },
];

/** État minimal consommé par la logique (sous-ensemble de study/status). */
export interface StudyStatusLite {
  locked: boolean;
  sujets: number;
  entrees_signees: number;
  requetes_ouvertes: number;
}

/**
 * Phase active dérivée de l'état réel (pas d'horloge mondiale) :
 * - base non verrouillée → R6 (inclusions/monitoring) ;
 * - verrouillé → R7 (analyse + rapport clinique) ;
 * - l'entrée en R8 est une décision humaine (notifié) — non dérivable.
 */
export function activePhase(status: StudyStatusLite): string {
  return status.locked ? "R7" : "R6";
}

export interface LockReadiness {
  ready: boolean;
  blocages: string[];
}

/**
 * Lisibilité du verrou M+18 — réplique exacte des préconditions serveur
 * (POST /study/lock) pour un affichage honnête AVANT l'action :
 * zéro requête SDV ouverte, au moins un sujet, au moins une entrée signée.
 */
export function lockReadiness(status: StudyStatusLite): LockReadiness {
  const blocages: string[] = [];
  if (status.requetes_ouvertes > 0) {
    blocages.push(
      `${status.requetes_ouvertes} requête(s) de monitoring ouverte(s) — clôture requise (plan-monitoring §5)`,
    );
  }
  if (status.sujets === 0) {
    blocages.push("aucun sujet inclus — verrouiller une base vide n'a pas de sens");
  } else if (status.entrees_signees === 0) {
    blocages.push("aucune entrée signée — rien à figer (checksum vide)");
  }
  return { ready: blocages.length === 0, blocages };
}

/** Checksum affiché de façon compacte (8 premiers + … + 8 derniers). */
export function formatChecksum(cs: string | undefined | null): string {
  if (!cs) return "—";
  if (cs.length <= 20) return cs;
  return `${cs.slice(0, 8)}…${cs.slice(-8)}`;
}

/** Résultat de validation du formulaire de verrouillage. */
export interface LockForm {
  temoin1: string;
  temoin2: string;
  declaration: string;
  confirmation: string;
}

/**
 * Validation client du lock — la garde serveur reste fail-closed
 * (≥ 2 témoins, RBAC ecrf.lock, 409 irréversible) ; ici on n'arme le
 * bouton que si l'opérateur a tapé la phrase de confirmation exacte.
 */
export function lockPayload(
  form: LockForm,
  studyCode: string,
): { ok: boolean; body?: { temoins: string[]; declaration: string }; errors: string[] } {
  const errors: string[] = [];
  const t1 = form.temoin1.trim();
  const t2 = form.temoin2.trim();
  if (!t1 || !t2) errors.push("les deux témoins sont requis (protocole §8)");
  else if (t1.toLowerCase() === t2.toLowerCase())
    errors.push("les deux témoins doivent être des personnes distinctes");
  if (form.confirmation !== `VERROU ${studyCode}`)
    errors.push(`confirmation incorrecte — taper « VERROU ${studyCode} »`);
  if (errors.length) return { ok: false, errors };
  return {
    ok: true,
    body: { temoins: [t1, t2], declaration: form.declaration.trim() },
    errors,
  };
}

/** Libellé du site depuis le catalogue (repli honnête si inconnu). */
export function siteLabel(
  sites: Record<string, string> | undefined,
  code: string,
): string {
  return sites?.[code] ?? `site inconnu (${code})`;
}
