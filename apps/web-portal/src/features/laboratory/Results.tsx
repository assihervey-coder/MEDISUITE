import { useEffect, useState } from "react";
import { api } from "../../services/api";

interface Result {
  id: string;
  valeur: number;
  unite: string;
  reference: string;
  flag: string;
  critical: boolean;
  valide_par: string;
}

/** Résultats de laboratoire : flags de référence + valeurs critiques visibles. */
export default function Results() {
  const [rows, setRows] = useState<Result[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const orders = await api.get<Array<{ id: string }>>("/api/lab/api/v1/orders");
        const results: Result[] = [];
        // en v0.1 : les résultats passent par la validation — on liste les commandes
        // avec leur statut ; l'endpoint /results complet arrive avec la paginatio v0.2
        for (const o of orders.slice(0, 20)) {
          const detail = await api
            .get<{ results?: Result[] }>(`/api/lab/api/v1/orders/${o.id}`)
            .catch(() => null);
          if (detail?.results) results.push(...detail.results);
        }
        setRows(results);
      } catch (e) {
        setError((e as Error).message);
      }
    })();
  }, []);

  return (
    <div>
      <h2>Laboratoire — résultats & contrôles qualité</h2>
      {error && <p className="error">laboratory-service injoignable : {error}</p>}
      <table>
        <thead>
          <tr><th>Valeur</th><th>Référence</th><th>Flag</th><th>Validé par</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.valeur} {r.unite}</td>
              <td>{r.reference}</td>
              <td>
                <span className={`badge ${r.critical ? "critical" : r.flag === "normal" ? "ok" : "warn"}`}>
                  {r.critical ? "CRITIQUE — notifier" : r.flag}
                </span>
              </td>
              <td>{r.valide_par || "en attente"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="note" style={{ marginTop: 12 }}>
        Workflow : ORDERED → COLLECTED → RESULTED → VALIDATED · QC Westgard (1₃ₛ, 2₂ₛ, R₄ₛ…)
        exécuté côté service. Les valeurs critiques déclenchent l'événement
        <code> alert.clinical</code> → SMS + in-app (notification-service).
      </p>
    </div>
  );
}
