import { useEffect, useState } from "react";
import { api } from "../services/api";

interface CaseRow {
  id: string;
  patient_nom: string;
  titre: string;
  severite: string;
  statut: string;
}

/** Panel clinique générique : branché sur n'importe lequel des 24 modules
 *  de spécialité (même contrat — ADR-0020). Affiche cas + scores disponibles. */
export default function ClinicalPanel({
  title,
  servicePath,
}: {
  title: string;
  servicePath: string;
}) {
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [info, setInfo] = useState<{ scores: string[] } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const slug = servicePath.replace("module/", "");
    api
      .get<{ scores: string[] }>(`/api/specialty/${slug}/module-info`)
      .then(setInfo)
      .catch((e) => setError(e.message));
    api
      .get<CaseRow[]>(`/api/specialty/${slug}/api/v1/cases`)
      .then(setCases)
      .catch(() => setCases([]));
  }, [servicePath]);

  return (
    <div>
      <h2>{title}</h2>
      {error && <p className="error">service injoignable ({error})</p>}
      {info && (
        <p className="note">
          Scores cliniques disponibles :{" "}
          {info.scores.map((s) => (
            <code key={s} style={{ marginRight: 6 }}>{s}</code>
          ))}
        </p>
      )}
      <table>
        <thead>
          <tr><th>Patient</th><th>Cas</th><th>Sévérité</th><th>Statut</th></tr>
        </thead>
        <tbody>
          {cases.map((c) => (
            <tr key={c.id}>
              <td>{c.patient_nom || "—"}</td>
              <td>{c.titre}</td>
              <td>
                <span className="badge warn">{c.severite || "à évaluer"}</span>
              </td>
              <td>{c.statut}</td>
            </tr>
          ))}
          {!cases.length && !error && (
            <tr><td colSpan={4} className="note">Aucun cas — démarrer le service (make dev-up)</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
