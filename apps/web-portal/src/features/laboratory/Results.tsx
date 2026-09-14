import { useEffect, useState } from "react";
import { api } from "../../services/api";

interface Order {
  id: string;
  patient_dossier: string;
  patient_nom: string;
  analyte: string;
  prescripteur: string;
  urgent: boolean;
  statut: string; // ORDERED → COLLECTED → RESULTED → VALIDATED
}

interface Result {
  id: string;
  analyte: string;
  patient_nom: string;
  patient_dossier: string;
  valeur: number;
  unite: string;
  reference: string;
  flag: string;
  critical: boolean;
  delta_pct: number | null;
  valide_par: string;
  statut: string;
}

const STATUT_BADGE: Record<string, string> = {
  ORDERED: "warn", COLLECTED: "ok", RESULTED: "ok", VALIDATED: "ok",
};

/** Laboratoire : prescriptions (workflow interactif — prélèvement) + résultats
 *  avec flags de référence, valeurs critiques et validation biologiste. */
export default function Results() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [rows, setRows] = useState<Result[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  async function load() {
    try {
      const [o, r] = await Promise.all([
        api.get<Order[]>("/api/lab/api/v1/orders"),
        api.get<Result[]>("/api/lab/api/v1/results"),
      ]);
      setOrders(o);
      setRows(r);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  /** Prélèvement : ORDERED → COLLECTED (génère le code-barres du tube). */
  async function collect(o: Order) {
    setBusy(o.id);
    setError("");
    try {
      const res = await api.post<{ barcode: string }>(
        `/api/lab/api/v1/orders/${o.id}/collect`, {});
      setOrders((prev) =>
        prev.map((x) => (x.id === o.id ? { ...x, statut: "COLLECTED" } : x)));
      window.alert(`Prélèvement enregistré — code-barres ${res.barcode}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }

  return (
    <div>
      <h2>Laboratoire — prescriptions, résultats & contrôles qualité</h2>
      {error && <p className="error">laboratory-service : {error}</p>}

      <h3 style={{ marginTop: 18 }}>Prescriptions ({orders.length})</h3>
      <table>
        <thead>
          <tr>
            <th>Analyte</th><th>Patient</th><th>Prescripteur</th>
            <th>Urgent</th><th>Statut</th><th></th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td><strong>{o.analyte}</strong></td>
              <td>{o.patient_nom} <code>{o.patient_dossier}</code></td>
              <td>{o.prescripteur || "—"}</td>
              <td>{o.urgent ? <span className="badge critical">URGENT</span> : "—"}</td>
              <td><span className={`badge ${STATUT_BADGE[o.statut] ?? ""}`}>{o.statut}</span></td>
              <td>
                {o.statut === "ORDERED" && (
                  <button
                    onClick={() => collect(o)}
                    disabled={busy === o.id}
                    style={{ fontSize: 12, padding: "4px 8px" }}
                  >
                    {busy === o.id ? "…" : "Prélever"}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 style={{ marginTop: 22 }}>Résultats ({rows.length})</h3>
      <table>
        <thead>
          <tr>
            <th>Analyte</th><th>Patient</th><th>Valeur</th><th>Référence</th>
            <th>Flag</th><th>Statut</th><th>Validé par</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td><strong>{r.analyte}</strong></td>
              <td>{r.patient_nom}</td>
              <td>
                {r.valeur} {r.unite}
                {r.delta_pct !== null && (
                  <span className="sub"> (Δ {r.delta_pct > 0 ? "+" : ""}{r.delta_pct} %)</span>
                )}
              </td>
              <td>{r.reference}</td>
              <td>
                <span className={`badge ${r.critical ? "critical" : r.flag === "normal" ? "ok" : "warn"}`}>
                  {r.critical ? "CRITIQUE — notifier" : r.flag}
                </span>
              </td>
              <td>{r.statut === "VALIDATED" ? "final" : "préliminaire"}</td>
              <td>{r.valide_par || "en attente biologiste"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="note" style={{ marginTop: 12 }}>
        Workflow : ORDERED → COLLECTED → RESULTED → VALIDATED · QC Westgard (1₃ₛ, 2₂ₛ, R₄ₛ…)
        exécuté côté service. Les valeurs critiques déclenchent l'événement
        <code> alert.clinical</code> → SMS + in-app (notification-service). La validation
        biologiste (RBAC <code>lab.validate</code>) s'effectue via
        <code> POST /api/v1/results/&#123;id&#125;/validate</code> (compte biologiste démo).
      </p>
    </div>
  );
}
