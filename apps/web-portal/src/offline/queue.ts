/**
 * Rejeu de la file offline (v0.7) — logique synchronisation.
 *
 * Le rejeu est idempotent : chaque opération porte une clé unique
 * (Idempotency-Key) et le serveur eCRF dédoublonne aussi par contenu
 * (clé calculée SHA-256). Une opération réussie est retirée ; un rejet
 * définitif 4xx (hors 408/429) part en « dead letter » pour inspection ;
 * une erreur réseau est conservée avec back-off exponentiel.
 */
import { useAuth } from "../store/authStore";
import { ApiError } from "../services/api";
import {
  type QueuedOp,
  countDead,
  enqueue,
  listPending,
  moveToDead,
  removePending,
} from "./db";
import { useOfflineStore } from "./offlineStore";
import { isPermanentRejection, newClientKey, retryDelayMs } from "./rules";

export { isPermanentRejection, newClientKey, retryDelayMs };

/** Empile une mutation pour rejeu ultérieur. */
export async function queueMutation(
  method: QueuedOp["method"],
  path: string,
  body: unknown,
): Promise<string> {
  const key = newClientKey();
  await enqueue({ key, method, path, body, createdAt: Date.now() });
  await refreshCounters();
  return key;
}

async function refreshCounters(): Promise<void> {
  const pending = (await listPending()).length;
  const dead = await countDead();
  useOfflineStore.getState().setCounters(pending, dead);
}

export interface ReplaySummary {
  attempted: number;
  sent: number;
  dead: number;
  remaining: number;
}

/** Rejoue la file ; jamais levant (les erreurs sont des statuts). */
export async function replayAll(
  fetchImpl: typeof fetch = fetch,
): Promise<ReplaySummary> {
  const store = useOfflineStore.getState();
  if (store.syncing) return { attempted: 0, sent: 0, dead: 0, remaining: -1 };
  store.setSyncing(true);
  try {
    const ops = await listPending();
    let sent = 0;
    let dead = 0;
    for (const op of ops) {
      const outcome = await replayOne(op, fetchImpl);
      if (outcome === "sent") sent += 1;
      else if (outcome === "dead") dead += 1;
    }
    await refreshCounters();
    const remaining = (await listPending()).length;
    if (sent > 0) useOfflineStore.getState().setLastSync(Date.now());
    return { attempted: ops.length, sent, dead, remaining };
  } finally {
    useOfflineStore.getState().setSyncing(false);
  }
}

async function replayOne(
  op: QueuedOp,
  fetchImpl: typeof fetch,
): Promise<"sent" | "dead" | "retry"> {
  const token = useAuth.getState().token;
  try {
    const res = await fetchImpl(op.path, {
      method: op.method,
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": op.key,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: op.body === undefined ? undefined : JSON.stringify(op.body),
    });
    if (res.ok) {
      if (op.id !== undefined) await removePending(op.id);
      return "sent";
    }
    if (isPermanentRejection(res.status)) {
      await moveToDead(op);
      return "dead";
    }
    return "retry"; // 408/429/5xx : rejeu plus tard
  } catch (err) {
    // erreur réseau : la saisie offline reste en file (sécurité clinique)
    op.tries += 1;
    op.lastError = err instanceof Error ? err.message : String(err);
    return "retry";
  }
}

/** Convertit une ApiError 503-ish en information de file (UI). */
export function describeQueuedError(err: unknown): string | null {
  if (err instanceof ApiError && err.status === 0) return err.message;
  return null;
}
