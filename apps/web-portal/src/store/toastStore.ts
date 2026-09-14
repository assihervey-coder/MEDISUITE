/** Store de notifications toast (nice-to-have) — file globale, auto-dismiss. */
import { create } from "zustand";

export interface Toast {
  id: number;
  kind: "ok" | "warn" | "error";
  message: string;
}

interface ToastState {
  toasts: Toast[];
  push: (kind: Toast["kind"], message: string) => void;
  dismiss: (id: number) => void;
}

let nextId = 1;

export const useToasts = create<ToastState>((set) => ({
  toasts: [],
  push: (kind, message) => {
    const id = nextId++;
    set((s) => ({ toasts: [...s.toasts, { id, kind, message }] }));
    // auto-dismiss 4,5 s (les erreurs restent 7 s — plus de temps pour lire)
    const ttl = kind === "error" ? 7000 : 4500;
    window.setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), ttl);
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

/** Raccourci d'usage : toast.ok("dossier créé"). */
export const toast = {
  ok: (m: string) => useToasts.getState().push("ok", m),
  warn: (m: string) => useToasts.getState().push("warn", m),
  error: (m: string) => useToasts.getState().push("error", m),
};
