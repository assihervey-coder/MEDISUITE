/**
 * Démarrage de la boucle de synchronisation offline (v0.7).
 *
 * - événements `online` / `offline` du navigateur ;
 * - rejeu immédiat au retour du réseau ;
 * - rejeu périodique (30 s) tant que des opérations restent en file
 *   (back-off long côté serveur ou réseau instable CHU) ;
 * - rafraîchissement des compteurs au montage.
 */
import { replayAll } from "./queue";
import { useOfflineStore } from "./offlineStore";
import { listPending } from "./db";
import { countDead } from "./db";

let started = false;

export function startOfflineSync(): void {
  if (started || typeof window === "undefined") return;
  started = true;
  const store = useOfflineStore.getState();

  window.addEventListener("online", () => {
    useOfflineStore.getState().setOnline(true);
    void replayAll();
  });
  window.addEventListener("offline", () =>
    useOfflineStore.getState().setOnline(false),
  );
  useOfflineStore.getState().setOnline(navigator.onLine);

  window.setInterval(() => {
    const s = useOfflineStore.getState();
    if (s.online && s.pending > 0 && !s.syncing) void replayAll();
  }, 30_000);

  // compteurs initiaux (ops persistées lors d'une session précédente)
  void Promise.all([listPending(), countDead()]).then(([pending, dead]) => {
    useOfflineStore.getState().setCounters(pending.length, dead);
  });
  void store; // store lu à chaque rejeu via getState()
}
