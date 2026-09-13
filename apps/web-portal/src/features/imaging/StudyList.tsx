import { useEffect, useState } from "react";
import { api } from "../../services/api";

interface Study {
  id: string;
  study_uid: string;
  accession_number: string;
  modality: string;
  description: string;
  study_date: string;
  statut: string;
}

/** Liste des études DICOM (QIDO-RS simplifiée) avec workflow de compte-rendu. */
export default function StudyList() {
  const [studies, setStudies] = useState<Study[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<Study[]>("/api/imaging/api/v1/studies")
      .then(setStudies)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h2>Imagerie médicale — DICOMweb (PS3.18)</h2>
      {error && <p className="error">imaging-service injoignable : {error}</p>}
      <table>
        <thead>
          <tr><th>Accession</th><th>Modalité</th><th>Description</th><th>Date</th><th>Statut</th><th>UID</th></tr>
        </thead>
        <tbody>
          {studies.map((s) => (
            <tr key={s.id}>
              <td><code>{s.accession_number}</code></td>
              <td><span className="badge ok">{s.modality}</span></td>
              <td>{s.description}</td>
              <td>{s.study_date}</td>
              <td>
                <span className={`badge ${s.statut === "SIGNED" ? "ok" : s.statut === "REPORTED" ? "warn" : "critical"}`}>
                  {s.statut}
                </span>
              </td>
              <td style={{ fontSize: 11, color: "#5a7a96" }}>{s.study_uid.slice(0, 28)}…</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="note" style={{ marginTop: 12 }}>
        QIDO-RS : <code>GET /dicom-web/studies</code> · STOW-RS : <code>POST /dicom-web/studies</code> ·
        WADO-RS : <code>GET /dicom-web/studies/&#123;uid&#125;/metadata</code>.
        Visualiseur OHIF : extension dicom-viewer (apps/dicom-viewer) — PACS Orthanc en prod.
      </p>
    </div>
  );
}
