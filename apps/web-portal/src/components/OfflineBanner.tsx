/** Bannière d'état offline (v0.7) : hors-ligne / file en attente / sync. */
import { useEffect, type CSSProperties } from "react";
import { useOfflineStore } from "../offline/offlineStore";
import { replayAll } from "../offline/queue";
import { startOfflineSync } from "../offline/sync";

export default function OfflineBanner() {
  const { online, pending, dead, syncing, lastSync } = useOfflineStore();

  useEffect(() => {
    startOfflineSync();
  }, []);

  if (online && pending === 0 && dead === 0) return null;

  const style: CSSProperties = {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: "6px 16px",
    fontSize: 13,
    color: "#fff",
    background: online ? "#1d4ed8" : "#b45309",
  };

  const last = lastSync ? new Date(lastSync).toLocaleTimeString() : null;

  return (
    <div style={style} role="status">
      {!online && <strong>⚠️ Hors connexion — saisie locale activée</strong>}
      {online && pending > 0 && <strong>🔄 Synchronisation…</strong>}
      <span>
        {pending > 0
          ? `${pending} saisie(s) en attente de sync${dead > 0 ? ` · ${dead} rejetée(s) à inspecter` : ""}`
          : dead > 0
            ? `${dead} saisie(s) rejetée(s) par le serveur`
            : "Données locales synchronisées"}
        {last ? ` · dernière sync ${last}` : ""}
      </span>
      {online && pending > 0 && (
        <button
          onClick={() => void replayAll()}
          disabled={syncing}
          style={{ background: "rgba(255,255,255,.2)", border: "none",
                   color: "#fff", padding: "2px 10px", borderRadius: 4,
                   cursor: "pointer" }}
        >
          {syncing ? "En cours…" : "Synchroniser maintenant"}
        </button>
      )}
    </div>
  );
}
