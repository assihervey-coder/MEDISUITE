import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../services/api";
import { downloadCsv, toCsv } from "../../utils/csv";
import { toast } from "../../store/toastStore";

interface Patient {
  id: string;
  numero_dossier: string;
  nom: string;
  prenoms: string;
  sexe: string;
  age: number;
  commune: string;
  cnam: string;
  consent_ia: boolean;
}

/** Liste des dossiers patients + création + consentement IA (RGPD). */
export default function PatientList() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [q, setQ] = useState("");
  const [error, setError] = useState("");

  async function load(query = "") {
    try {
      setPatients(await api.get<Patient[]>(`/api/patients/api/v1/patients?q=${encodeURIComponent(query)}`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function toggleConsent(p: Patient) {
    try {
      await api.post(`/api/patients/api/v1/patients/${p.id}/consent`, { consent_ia: !p.consent_ia });
      toast.ok(`Consentement IA ${p.consent_ia ? "révoqué" : "accordé"} — ${p.nom}`);
    } catch (e) {
      toast.error((e as Error).message);
    }
    load(q);
  }

  /** Export CSV de la liste courante (good-to-have) — découpage rapide
   *  pour statistiques de service / rapports Direction. */
  function exportCsv() {
    downloadCsv(
      "patients-medisuite.csv",
      toCsv(patients as unknown as Array<Record<string, unknown>>,
        ["numero_dossier", "nom", "prenoms", "sexe", "age", "commune", "cnam", "consent_ia"]),
    );
    toast.ok(`${patients.length} dossier(s) exporté(s) en CSV`);
  }

  async function create(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget; // capturé AVANT le await (null après)
    const f = new FormData(form);
    try {
      await api.post("/api/patients/api/v1/patients", {
        nom: f.get("nom"), prenoms: f.get("prenoms"), sexe: f.get("sexe"),
        date_naissance: f.get("naissance"), commune: f.get("commune"),
      });
      form.reset();
      toast.ok("Dossier patient créé");
    } catch (err) {
      toast.error(`Création impossible : ${(err as Error).message}`);
    }
    load(q);
  }

  return (
    <div>
      <h2>Dossiers patients</h2>
      {error && <p className="error">{error}</p>}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          load(q);
        }}
        style={{ display: "flex", gap: 8, marginBottom: 14 }}
      >
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Nom ou n° dossier…" />
        <button type="submit">Rechercher</button>
        <button type="button" onClick={exportCsv} disabled={patients.length === 0} title="Export CSV (Excel/LibreOffice)">
          ⬇ Export CSV
        </button>
      </form>
      <table>
        <thead>
          <tr>
            <th>Dossier</th><th>Nom & prénoms</th><th>Sexe</th><th>Âge</th>
            <th>Commune</th><th>CNAM</th><th>Consent. IA</th><th></th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p) => (
            <tr key={p.id}>
              <td><code>{p.numero_dossier}</code></td>
              <td>
                <Link to={`/patients/${p.id}`}>
                  {p.nom} {p.prenoms}
                </Link>
              </td>
              <td>{p.sexe}</td>
              <td>{p.age}</td>
              <td>{p.commune}</td>
              <td>{p.cnam || "—"}</td>
              <td>
                <span className={`badge ${p.consent_ia ? "ok" : "warn"}`}>
                  {p.consent_ia ? "accordé" : "refusé"}
                </span>
              </td>
              <td>
                <button onClick={() => toggleConsent(p)} style={{ fontSize: 12, padding: "4px 8px" }}>
                  {p.consent_ia ? "Révoquer" : "Accorder"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <h3 style={{ marginTop: 22 }}>Nouveau patient</h3>
      <p className="note" style={{ marginTop: 0 }}>
        Astuce : cliquez sur un nom pour ouvrir la <strong>fiche détaillée</strong>
        (consultations, diagnostics CIM-10, consentements, export FHIR).
      </p>
      <form onSubmit={create} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <input name="nom" placeholder="Nom" required />
        <input name="prenoms" placeholder="Prénoms" required />
        <select name="sexe" defaultValue="F">
          <option value="F">F</option><option value="M">M</option>
        </select>
        <input name="naissance" type="date" required />
        <input name="commune" placeholder="Commune (ex. Yopougon)" />
        <button type="submit">Créer le dossier</button>
      </form>
    </div>
  );
}
