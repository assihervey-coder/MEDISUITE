/** État offline global du portal (zustand) — consommé par OfflineBanner. */
import { create } from "zustand";

interface OfflineState {
  online: boolean;
  pending: number;
  dead: number;
  syncing: boolean;
  lastSync: number | null;
  setOnline: (online: boolean) => void;
  setCounters: (pending: number, dead: number) => void;
  setSyncing: (syncing: boolean) => void;
  setLastSync: (ts: number) => void;
}

export const useOfflineStore = create<OfflineState>((set) => ({
  online: typeof navigator === "undefined" ? true : navigator.onLine,
  pending: 0,
  dead: 0,
  syncing: false,
  lastSync: null,
  setOnline: (online) => set({ online }),
  setCounters: (pending, dead) => set({ pending, dead }),
  setSyncing: (syncing) => set({ syncing }),
  setLastSync: (lastSync) => set({ lastSync }),
}));
