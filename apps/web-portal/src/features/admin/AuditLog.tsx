import { useEffect, useState } from "react";
import { api } from "../../services/api";

interface ChainRow {
  index: number;
  action: string;
  actor: string;
  resource: string;
  hash: string;
}

/** Registre d'audit à chaîne de hachage : traçabilité + vérification d'intégrité. */
export default function AuditLog() {
  const [rows, setRows] = useState<ChainRow[]>([]);
  const [verdict, setVerdict] = useState<string>("");
  const [error, setError] = useState("");

  async function load() {
    try {
      setRows(await api.get<ChainRow[]>("/api/audit/api/v1/tail?n=25"));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function verify() {
    const v = await api.post<{ integre: boolean; nb_events: number }>("/api/audit/api/v1/chain/verify");
    setVerdict(
      v.integre
        ? `✅ Chaîne intègre — ${v.nb_events} événements vérifiés`
        : "❌ ALTÉRATION DÉTECTÉE — investigation requise (runbook rb-004)"
    );
  }

  return (
    <div>
      <h2>Registre d'audit — chaîne de hachage SHA-256</h2>
      <button onClick={verify}>Vérifier l'intégrité de la chaîne</button>
      {verdict && <p><strong>{verdict}</strong></p>}
      {error && <p className="error">audit-service injoignable : {error}</p>}
      <table style={{ marginTop: 14 }}>
        <thead>
          <tr><th>#</th><th>Action</th><th>Acteur</th><th>Ressource</th><th>Hash</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.index}>
              <td>{r.index}</td>
              <td><code>{r.action}</code></td>
              <td>{r.actor}</td>
              <td>{r.resource}</td>
              <td style={{ fontSize: 11, color: "#5a7a96" }}>{r.hash}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="note" style={{ marginTop: 12 }}>
        Chaque événement chaîne le précédent : toute falsification rétroactive casse la
        vérification (démonstration : <code>POST /api/v1/chain/tamper-demo/2</code>).
        Exigence de traçabilité IEC 81001-5-1.
      </p>
    </div>
  );
}
