import { useEffect, useState } from "react";
import { api } from "../../services/api";

interface Kpis {
  patients: number | null;
  etudes_imagerie: number | null;
  prescriptions_labo: number | null;
  resultats_valides: number | null;
  comptes_rendus: number | null;
  consultations: number | null;
}

/** Tableau de bord : KPIs agrégés en lecture-seule par analytics-service. */
export default function MainDashboard() {
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<Kpis>("/api/analytics/api/v1/kpis")
      .then(setKpis)
      .catch((e) => setError(e.message));
  }, []);

  const cards: Array<[string, number | null | undefined, string]> = [
    ["Dossiers patients", kpis?.patients, "patient-service"],
    ["Consultations", kpis?.consultations, "encounters"],
    ["Études d'imagerie", kpis?.etudes_imagerie, "imaging-service (DICOMweb)"],
    ["Prescriptions labo", kpis?.prescriptions_labo, "laboratory-service"],
    ["Résultats validés", kpis?.resultats_valides, "double validation biologiste"],
    ["Comptes-rendus", kpis?.comptes_rendus, "reporting-service"],
  ];

  return (
    <div>
      <h2>Tableau de bord — santé publique ivoirienne</h2>
      {error && <p className="error">analytics-service injoignable : {error}</p>}
      <div className="cards">
        {cards.map(([label, value, sub]) => (
          <div className="card" key={label}>
            <h3>{label}</h3>
            <div className="kpi">{value ?? "—"}</div>
            <div className="sub">{sub}</div>
          </div>
        ))}
      </div>
      <p className="note" style={{ marginTop: 16 }}>
        Toutes les valeurs proviennent des bases des microservices (database-per-service,
        lecture seule). Démarrage : <code>make dev-up</code> puis <code>make smoke</code>.
      </p>
    </div>
  );
}
