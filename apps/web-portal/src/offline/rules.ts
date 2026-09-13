/**
 * Règles pures de la file offline (v0.7) — sans dépendance DOM ni store :
 * testables dans n'importe quel environnement (vitest node inclus).
 */

/** Back-off exponentiel plafonné : 1 s → 2 s → 4 s → … → 30 s. */
export function retryDelayMs(tries: number): number {
  return Math.min(30_000, 1_000 * 2 ** Math.max(0, tries));
}

/** 4xx non-rejouables : l'opération ne passera jamais seule. */
export function isPermanentRejection(status: number): boolean {
  return status >= 400 && status < 500 && status !== 408 && status !== 429;
}

/** Clé d'idempotence client (UUID quand disponible, fallback déterministe). */
export function newClientKey(): string {
  const c = globalThis.crypto as Crypto | undefined;
  if (c && typeof c.randomUUID === "function") return c.randomUUID();
  return `offline-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}
