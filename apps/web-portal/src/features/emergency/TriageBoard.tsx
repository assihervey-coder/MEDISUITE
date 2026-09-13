import { useEffect, useState } from "react";
import { api } from "../../services/api";

interface Case {
  id: string;
  patient_nom: string;
  titre: string;
  severite: string;
  statut: string;
}

/** Triage des urgences : ESI/CTMP via le moteur de règles cliniques. */
export default function TriageBoard() {
  const [cases, setCases] = useState<Case[]>([]);
  const [esiResult, setEsiResult] = useState<string>("");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<Case[]>("/api/specialty/emergency/api/v1/cases")
      .then(setCases)
      .catch((e) => setError(e.message));
  }, []);

  async function runEsi(ressources: number) {
    const r = await api.post<{ resultat: { niveau: number; couleur: string; libelle: string } }>(
      "/api/specialty/emergency/api/v1/scores/esi",
      { niveau_ressources: ressources, facteur_risque_haut: ressources <= 1 }
    );
    setEsiResult(
      `ESI ${r.resultat.niveau} — ${r.resultat.couleur.toUpperCase()} : ${r.resultat.libelle}`
    );
  }

  return (
    <div>
      <h2>Urgences — tableau de triage</h2>
      {error && <p className="error">emergency-service injoignable : {error}</p>}
      <div className="cards" style={{ marginBottom: 18 }}>
        {[1, 2, 3, 4].map((n) => (
          <div className="card" key={n}>
            <h3>Simulation ESI {n}</h3>
            <p className="sub">{n} ressource(s) prédite(s)</p>
            <button onClick={() => runEsi(n)}>Calculer</button>
          </div>
        ))}
      </div>
      {esiResult && <p><strong>Moteur clinique :</strong> {esiResult}</p>}
      <table>
        <thead>
          <tr><th>Patient</th><th>Motif</th><th>Sévérité</th><th>Statut</th></tr>
        </thead>
        <tbody>
          {cases.map((c) => (
            <tr key={c.id}>
              <td>{c.patient_nom || "—"}</td>
              <td>{c.titre}</td>
              <td>
                <span className={`badge ${c.severite === "critique" ? "critical" : "warn"}`}>
                  {c.severite || "à évaluer"}
                </span>
              </td>
              <td>{c.statut}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="note" style={{ marginTop: 12 }}>
        Scores disponibles : ESI 4e éd., CTMP ivoirien, qSOFA, Wells PE, Parkland, ISS,
        CURB-65, choc ATLS, shock index — moteur <code>packages/clinical-rules</code>.
      </p>
    </div>
  );
}
