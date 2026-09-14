/** Fiche patient détaillée (BEST TO HAVE) — identité complète, consentements,
 *  encounters (ajout), conditions CIM-10 (ajout), export FHIR R4 + pseudonyme.
 *  Cœur du dossier patient informatisé : tout part de cette fiche. */
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../services/api";
import { downloadFile } from "../../utils/csv";
import { toast } from "../../store/toastStore";

interface Patient {
  id: string; numero_dossier: string; nom: string; prenoms: string;
  sexe: string; date_naissance: string; age: number; telephone?: string;
  ville?: string; commune?: string; cnam?: string; groupe_sanguin?: string;
  consent_ia: boolean; consent_recherche?: boolean; pseudonyme: string;
}

interface Encounter {
  id: string; date: string; motif: string; classe: string;
  service?: string; prescripteur?: string;
}

interface Condition {
  id: string; cim10: string; libelle: string; severite: string; statut: string;
}

export default function PatientDetail() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [p, setP] = useState<Patient | null>(null);
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [conditions, setConditions] = useState<Condition[]>([]);
  const [error, setError] = useState("");
  const [fhirBusy, setFhirBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [detail, enc, con] = await Promise.all([
        api.get<Patient>(`/api/patients/api/v1/patients/${id}`),
        api.get<Encounter[]>(`/api/patients/api/v1/patients/${id}/encounters`),
        api.get<Condition[]>(`/api/patients/api/v1/patients/${id}/conditions`).catch(() => [] as Condition[]),
      ]);
      setP(detail);
      setEncounters(enc);
      setConditions(con);
      setError("");
    } catch (e) {
      setError((e as Error).message);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  async function addEncounter(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget; // capturé AVANT le await
    const f = new FormData(form);
    try {
      await api.post(`/api/patients/api/v1/patients/${id}/encounters`, {
        date: f.get("date"), motif: f.get("motif"), classe: f.get("classe"),
        service: f.get("service") ?? "", prescripteur: f.get("prescripteur") ?? "",
      });
      form.reset();
      toast.ok("Consultation enregistrée");
      load();
    } catch (err) {
      toast.error(`Échec encounter : ${(err as Error).message}`);
    }
  }

  async function addCondition(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    try {
      await api.post(`/api/patients/api/v1/patients/${id}/conditions`, {
        cim10: f.get("cim10"), libelle: f.get("libelle"),
        severite: f.get("severite") ?? "", statut: f.get("statut") ?? "active",
      });
      form.reset();
      toast.ok("Diagnostic CIM-10 ajouté");
      load();
    } catch (err) {
      toast.error(`Échec diagnostic : ${(err as Error).message}`);
    }
  }

  async function toggleConsent(field: "consent_ia" | "consent_recherche") {
    if (!p) return;
    const next = !p[field];
    try {
      await api.post(`/api/patients/api/v1/patients/${id}/consent`, { [field]: next });
      toast.ok(`${field === "consent_ia" ? "Consentement IA" : "Consentement recherche"} : ${next ? "accordé" : "révoqué"}`);
      load();
    } catch (err) {
      toast.error((err as Error).message);
    }
  }

  async function exportFhir() {
    setFhirBusy(true);
    try {
      const bundle = await api.get<unknown>(`/api/patients/api/v1/patients/${id}/fhir`);
      downloadFile(
        `fhir-patient-${p?.numero_dossier ?? id}.json`,
        JSON.stringify(bundle, null, 2),
      );
      toast.ok("Ressource FHIR R4 exportée");
    } catch (err) {
      toast.error(`Export FHIR : ${(err as Error).message}`);
    } finally {
      setFhirBusy(false);
    }
  }

  if (error) {
    return (
      <div>
        <h2>Fiche patient</h2>
        <p className="error">{error}</p>
        <Link to="/patients">← retour à la liste</Link>
      </div>
    );
  }
  if (!p) return <p className="note">Chargement de la fiche…</p>;

  return (
    <div>
      <p style={{ margin: "0 0 6px" }}>
        <Link to="/patients">← Dossiers patients</Link>
      </p>
      <h2>
        {p.nom} {p.prenoms}{" "}
        <span className={`badge ${p.sexe === "M" ? "ok" : "warn"}`}>{p.sexe}</span>{" "}
        <span className="badge">{p.age} ans</span>
      </h2>

      <div className="detail-grid">
        <div className="card">
          <h3>Identité &amp; contact</h3>
          <dl className="kv">
            <dt>N° dossier</dt><dd><code>{p.numero_dossier}</code></dd>
            <dt>Naissance</dt><dd>{p.date_naissance}</dd>
            <dt>Téléphone</dt><dd>{p.telephone || "—"}</dd>
            <dt>Commune</dt><dd>{p.commune || "—"}{p.ville ? ` (${p.ville})` : ""}</dd>
            <dt>CNAM</dt><dd>{p.cnam ? <code>{p.cnam}</code> : "—"}</dd>
            <dt>Groupe sanguin</dt><dd>{p.groupe_sanguin || "—"}</dd>
            <dt>Pseudonyme</dt><dd><code style={{ fontSize: 10 }}>{p.pseudonyme.slice(0, 24)}…</code></dd>
          </dl>
        </div>

        <div className="card">
          <h3>Consentements (RGPD / loi ivoirienne)</h3>
          <p>
            IA diagnostique :{" "}
            <span className={`badge ${p.consent_ia ? "ok" : "warn"}`}>
              {p.consent_ia ? "accordé" : "refusé"}
            </span>{" "}
            <button type="button" onClick={() => toggleConsent("consent_ia")} style={{ fontSize: 12, padding: "4px 8px" }}>
              {p.consent_ia ? "Révoquer" : "Accorder"}
            </button>
          </p>
          <p>
            Recherche clinique :{" "}
            <span className={`badge ${p.consent_recherche ? "ok" : "warn"}`}>
              {p.consent_recherche ? "accordé" : "refusé"}
            </span>{" "}
            <button type="button" onClick={() => toggleConsent("consent_recherche")} style={{ fontSize: 12, padding: "4px 8px" }}>
              {p.consent_recherche ? "Révoquer" : "Accorder"}
            </button>
          </p>
          <h3 style={{ marginTop: 16 }}>Interopérabilité</h3>
          <button type="button" onClick={exportFhir} disabled={fhirBusy}>
            {fhirBusy ? "Export…" : "⬇ Export FHIR R4 (JSON)"}
          </button>
          <p className="note" style={{ marginTop: 8 }}>
            Patient FHIR (<code>identifier</code> dossier + CNAM) — prêt pour
            DHIS2 / systèmes hospitaliers tiers.
          </p>
        </div>
      </div>

      <h3 style={{ marginTop: 24 }}>Consultations ({encounters.length})</h3>
      {encounters.length > 0 ? (
        <table>
          <thead>
            <tr><th>Date</th><th>Motif</th><th>Classe</th><th>Service</th><th>Prescripteur</th></tr>
          </thead>
          <tbody>
            {encounters.map((e) => (
              <tr key={e.id}>
                <td>{e.date}</td><td>{e.motif}</td>
                <td><span className="badge">{e.classe}</span></td>
                <td>{e.service || "—"}</td><td>{e.prescripteur || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="note">Aucune consultation enregistrée — ajoutez la première ci-dessous.</p>
      )}
      <form onSubmit={addEncounter} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
        <input name="date" type="date" required defaultValue={new Date().toISOString().slice(0, 10)} />
        <input name="motif" placeholder="Motif (ex. fièvre + céphalées)" required style={{ minWidth: 220 }} />
        <select name="classe" defaultValue="AMB" title="Classe encounter HL7 (AMB, EMER, IMP, …)">
          <option value="AMB">AMB — ambulatoire</option>
          <option value="EMER">EMER — urgences</option>
          <option value="IMP">IMP — hospitalisation</option>
          <option value="VR">VR — soins virtuels</option>
        </select>
        <input name="service" placeholder="Service (ex. médecine interne)" />
        <input name="prescripteur" placeholder="Prescripteur" />
        <button type="submit">+ Ajouter la consultation</button>
      </form>

      <h3 style={{ marginTop: 24 }}>Diagnostics CIM-10 ({conditions.length})</h3>
      {conditions.length > 0 ? (
        <table>
          <thead>
            <tr><th>Code</th><th>Libellé</th><th>Sévérité</th><th>Statut</th></tr>
          </thead>
          <tbody>
            {conditions.map((c) => (
              <tr key={c.id}>
                <td><code>{c.cim10}</code></td><td>{c.libelle}</td>
                <td>{c.severite ? <span className={`badge ${c.severite === "sévère" ? "critical" : "warn"}`}>{c.severite}</span> : "—"}</td>
                <td><span className={`badge ${c.statut === "active" ? "warn" : "ok"}`}>{c.statut}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="note">Aucun diagnostic codé — ajoutez-en un (code CIM-10).</p>
      )}
      <form onSubmit={addCondition} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
        <input name="cim10" placeholder="Code CIM-10 (ex. B50.9)" required style={{ maxWidth: 160 }} />
        <input name="libelle" placeholder="Libellé (ex. paludisme)" required style={{ minWidth: 220 }} />
        <select name="severite" defaultValue="">
          <option value="">— sévérité —</option>
          <option value="légère">légère</option>
          <option value="modérée">modérée</option>
          <option value="sévère">sévère</option>
        </select>
        <select name="statut" defaultValue="active">
          <option value="active">active</option>
          <option value="résolue">résolue</option>
        </select>
        <button type="submit">+ Ajouter le diagnostic</button>
      </form>

      <p className="note" style={{ marginTop: 18 }}>
        <button type="button" onClick={() => navigate(-1)} style={{ background: "transparent", color: "var(--muted)", padding: 0 }}>
          ← retour
        </button>
      </p>
    </div>
  );
}
