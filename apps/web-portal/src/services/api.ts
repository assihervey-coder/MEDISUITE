/** Client API unique : JWT injecté automatiquement, erreur typée. */
import { useAuth } from "../store/authStore";
import { queueMutation } from "../offline/queue";

/** Reçu d'une mutation empilée hors-ligne (rejeu idempotent au retour). */
export interface QueuedReceipt {
  __queued: true;
  clientKey: string;
}

export function isQueuedReceipt<T>(value: T | QueuedReceipt): value is QueuedReceipt {
  return (value as QueuedReceipt)?.__queued === true;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = useAuth.getState().token;
  const res = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (res.status === 401) {
    useAuth.getState().logout();
    throw new ApiError(401, "session expirée — reconnectez-vous");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? body.error ?? res.statusText);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

export const api = {
  get: <T,>(p: string) => request<T>(p),
  post: <T,>(p: string, body?: unknown) =>
    request<T>(p, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
};

/**
 * Soumission offline-first (v0.7) : hors connexion, la mutation est empilée
 * dans IndexedDB et rejouée automatiquement avec une clé d'idempotence —
 * le serveur eCRF dédoublonne (clé calculée), donc aucun doublon possible.
 * En ligne, comportement identique à api.post.
 */
export async function submitWithQueue<T>(path: string, body?: unknown): Promise<T | QueuedReceipt> {
  if (typeof navigator !== "undefined" && !navigator.onLine) {
    const clientKey = await queueMutation("POST", path, body ?? null);
    return { __queued: true, clientKey };
  }
  return api.post<T>(path, body);
}

/** Score clinique via un module de spécialité (réponse typée par l'appelant). */
export function postScore<T = unknown>(module: string, score: string, body: unknown): Promise<T> {
  return api.post<T>(`/api/specialty/${module}/api/v1/scores/${score}`, body);
}
