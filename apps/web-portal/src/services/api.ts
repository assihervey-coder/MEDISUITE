/** Client API unique : JWT injecté automatiquement, erreur typée. */
import { useAuth } from "../store/authStore";

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

/** Score clinique via un module de spécialité (réponse typée par l'appelant). */
export function postScore<T = unknown>(module: string, score: string, body: unknown): Promise<T> {
  return api.post<T>(`/api/specialty/${module}/api/v1/scores/${score}`, body);
}
