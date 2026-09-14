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

interface PacsStatus {
  reachable: boolean;
  url: string;
  erreur?: string;
  note?: string;
}

interface Integration {
  nom?: string;
  nom_service?: string;
  statut?: string;
  [k: string]: unknown;
}

/** Base du visualiseur OHIF v3 (v0.3) — surchargeable par VITE_OHIF_BASE. */
const OHIF_BASE = import.meta.env.VITE_OHIF_BASE ?? "http://localhost:3001";

/** Liste des études DICOM (QIDO-RS simplifiée) avec workflow de compte-rendu
 *  et ouverture du visualiseur OHIF v3 (lien profond /viewer?StudyInstanceUIDs). */
export default function StudyList() {
  const [studies, setStudies] = useState<Study[]>([]);
  const [error, setError] = useState("");
  const [pacs, setPacs] = useState<PacsStatus | null>(null);
  const [integrations, setIntegrations] = useState<Integration[]>([]);

  useEffect(() => {
    api
      .get<Study[]>("/api/imaging/api/v1/studies")
      .then(setStudies)
      .catch((e) => setError(e.message));
    // Statut PACS Orthanc + intégrations déclarées (good-to-have).
    api
      .get<PacsStatus>("/api/imaging/api/v1/pacs/status")
      .then(setPacs)
      .catch(() => setPacs(null));
    api
      .get<{ integrations?: Integration[] } | Integration[]>("/api/imaging/api/v1/integrations")
      .then((r) => setIntegrations(Array.isArray(r) ? r : (r.integrations ?? [])))
      .catch(() => setIntegrations([]));
  }, []);

  /** Lien profond OHIF : l'UID est encodé par imaging-service (viewer-url),
   *  mais on compose aussi côté client si l'API est hors ligne (mode dégradé). */
  function openInOhif(study: Study): void {
    const url = `${OHIF_BASE}/viewer?StudyInstanceUIDs=${encodeURIComponent(study.study_uid)}`;
    window.open(url, "_blank", "noopener");
  }

  return (
    <div>
      <h2>Imagerie médicale — DICOMweb (PS3.18)</h2>
      {error && <p className="error">imaging-service injoignable : {error}</p>}

      {/* Statut PACS temps réel (good-to-have) — indicateur réseau OHIF/Orthanc. */}
      {pacs && (
        <div className={`banner ${pacs.reachable ? "ok" : "warn"}`}>
          <h3>
            PACS Orthanc : {pacs.reachable ? "✅ joignable" : "⚠️ injoignable — imagerie locale consultable"}
          </h3>
          <p className="sub">
            <code>{pacs.url}</code>
            {pacs.erreur && <> — {pacs.erreur}</>}
            {pacs.note && <> · {pacs.note}</>}
          </p>
        </div>
      )}
      <table>
        <thead>
          <tr><th>Accession</th><th>Modalité</th><th>Description</th><th>Date</th><th>Statut</th><th>Viewer</th></tr>
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
              <td>
                <button type="button" onClick={() => openInOhif(s)}>
                  OHIF ↗
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {integrations.length > 0 && (
        <p className="note" style={{ marginTop: 10 }}>
          Intégrations :{" "}
          {integrations.map((i) => (
            <span key={(i.nom ?? i.nom_service) as string} className="badge" style={{ marginRight: 6 }}>
              {String(i.nom ?? i.nom_service)}{i.statut ? ` — ${i.statut}` : ""}
            </span>
          ))}
        </p>
      )}
      <p className="note" style={{ marginTop: 12 }}>
        QIDO-RS : <code>GET /dicom-web/studies</code> · STOW-RS : <code>POST /dicom-web/studies</code> ·
        WADO-RS : <code>GET /dicom-web/studies/&#123;uid&#125;/metadata</code>.
        Visualiseur diagnostique : <strong>OHIF v3</strong> branché sur <code>/dicom-web</code>
        {" "}(PACS Orthanc réel) — <code>docker compose up ohif-viewer</code>, UI sur le port 3001,
        lien profond généré par <code>/api/v1/pacs/viewer-url</code>.
      </p>
    </div>
  );
}
