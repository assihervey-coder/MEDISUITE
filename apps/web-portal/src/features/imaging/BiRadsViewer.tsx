/**
 * Lecteur BI-RADS — lecture mammographique structurée (ACR BI-RADS 5e éd. 2013).
 * Écran spécialisé d'imagerie : cotation ACR, sémiologie (masse, microcalcifications,
 * asymétrie, aire axillaire), catégorisation BI-RADS calculée par le moteur central
 * packages/clinical-rules via oncology-service (POST /api/v1/scores/birads).
 * L'aide à la décision affichée ne remplace pas le double lecture ni le jugement clinique.
 */
import { useEffect, useMemo, useState } from "react";
import { api, postScore } from "../../services/api";

interface CaseRow {
  id: string;
  patient_nom: string;
  titre: string;
  date: string;
  statut: string;
}

interface BiradsResult {
  categorie: string;
  conduite: string;
  densite_acr: string;
}

const MICROCALC_OPTIONS = ["aucune", "bénignes", "indéterminées", "suspectes"] as const;
type Microcalc = (typeof MICROCALC_OPTIONS)[number];

const ACR_OPTIONS: Array<{ key: "a" | "b" | "c" | "d"; label: string }> = [
  { key: "a", label: "A — seins denses" },
  { key: "b", label: "B — densité hétérogène" },
  { key: "c", label: "C — dense hétérogène (altère sensibilité)" },
  { key: "d", label: "D — extrêmement dense" },
];

/** Couleur de la catégorie BI-RADS : 1-2 bénin, 3 probablement bénin, 4 suspect, 5 hautement suspect. */
function biradsLevel(cat: number): "ok" | "warn" | "critical" {
  if (cat <= 2) return "ok";
  if (cat === 3) return "warn";
  return "critical";
}

export default function BiRadsViewer() {
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<CaseRow | null>(null);

  // Lecture structurée
  const [densite, setDensite] = useState<"a" | "b" | "c" | "d">("b");
  const [masse, setMasse] = useState(false);
  const [microcalc, setMicrocalc] = useState<Microcalc>("aucune");
  const [asymetrie, setAsymetrie] = useState(false);
  const [axillaire, setAxillaire] = useState(false);

  const [result, setResult] = useState<BiradsResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .get<CaseRow[]>("/api/specialty/oncology/api/v1/cases")
      .then((rows) => setCases(rows.slice(0, 8)))
      .catch((e) => setError(e.message));
  }, []);

  const catNumber = useMemo(() => {
    if (!result) return null;
    const m = result.categorie.match(/(\d+)/);
    return m ? Number(m[1]) : null;
  }, [result]);

  async function evaluate() {
    setBusy(true);
    setError("");
    try {
      const r = await postScore<{ resultat: BiradsResult }>("oncology", "birads", {
        masse,
        microcalcifications: microcalc,
        asymetrie,
        aire_axillaire: axillaire,
        densite_acr: densite,
      });
      setResult(r.resultat);
    } catch (e) {
      setError(e instanceof Error ? e.message : "échec de l'évaluation");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2>🎗️ Lecteur BI-RADS — lecture mammographique structurée</h2>
      <p className="note">
        Cotation BI-RADS 5<sup>e</sup> édition (ACR 2013) — moteur{" "}
        <code>packages/clinical-rules</code> via oncology-service. Double lecture obligatoire
        avant toute décision.
      </p>
      {error && <p className="error">oncology-service : {error}</p>}

      <div className="birads-layout">
        {/* Colonne gauche : dossiers + formulaire de lecture */}
        <div className="card">
          <h3>Dossiers sénologie (module oncologie)</h3>
          <table>
            <thead>
              <tr><th>Patient</th><th>Examen</th><th>Date</th></tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => setSelected(c)}
                  className={selected?.id === c.id ? "row-selected" : undefined}
                >
                  <td>{c.patient_nom || "—"}</td>
                  <td>{c.titre}</td>
                  <td>{c.date}</td>
                </tr>
              ))}
              {cases.length === 0 && (
                <tr><td colSpan={3}>Aucun dossier (service hors ligne ?)</td></tr>
              )}
            </tbody>
          </table>

          <h3 style={{ marginTop: 16 }}>Lecture structurée {selected ? `— ${selected.patient_nom}` : ""}</h3>
          <div className="form-grid">
            <label>
              Densité mammaire (ACR)
              <select value={densite} onChange={(e) => setDensite(e.target.value as typeof densite)}>
                {ACR_OPTIONS.map((o) => (
                  <option key={o.key} value={o.key}>{o.label}</option>
                ))}
              </select>
            </label>
            <label>
              Microcalcifications
              <select value={microcalc} onChange={(e) => setMicrocalc(e.target.value as Microcalc)}>
                {MICROCALC_OPTIONS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </label>
            <label className="chk">
              <input type="checkbox" checked={masse} onChange={(e) => setMasse(e.target.checked)} />
              Masse / opacité
            </label>
            <label className="chk">
              <input type="checkbox" checked={asymetrie} onChange={(e) => setAsymetrie(e.target.checked)} />
              Asymétrie de densité
            </label>
            <label className="chk">
              <input type="checkbox" checked={axillaire} onChange={(e) => setAxillaire(e.target.checked)} />
              Aire axillaire suspecte
            </label>
          </div>
          <button onClick={evaluate} disabled={busy} style={{ marginTop: 12 }}>
            {busy ? "Évaluation…" : "Évaluer BI-RADS"}
          </button>
        </div>

        {/* Colonne droite : résultat + échelle */}
        <div>
          <div className="card">
            <h3>Catégorisation</h3>
            {!result && <p className="note">Renseignez la sémiologie puis lancez l'évaluation.</p>}
            {result && catNumber !== null && (
              <>
                <div className="birads-verdict">
                  <span className={`badge ${biradsLevel(catNumber)} birads-badge`}>
                    {result.categorie}
                  </span>
                  <span className="sub">densité ACR {result.densite_acr.toUpperCase()}</span>
                </div>
                <p style={{ margin: "10px 0 4px" }}>
                  <strong>Conduite à tenir :</strong> {result.conduite}
                </p>
                <div className="birads-scale" aria-label="échelle BI-RADS 1 à 6">
                  {[1, 2, 3, 4, 5, 6].map((n) => (
                    <div
                      key={n}
                      className={`birads-step ${biradsLevel(n)} ${n === catNumber ? "current" : ""}`}
                      title={
                        ["", "négatif", "bénin", "probablement bénin", "suspect — biopsie", "hautement suspect", "biopsie prouvée"][n]
                      }
                    >
                      {n}
                    </div>
                  ))}
                </div>
                <p className="note" style={{ marginTop: 8 }}>
                  1-2 : surveillance habituelle · 3 : contrôle 6 mois · 4 : biopsie · 5 : biopsie
                  en urgence relative · 6 : cancer prouvé (histologie).
                </p>
              </>
            )}
          </div>
          <div className="card" style={{ marginTop: 16 }}>
            <h3>Rappels sémiologiques</h3>
            <ul className="note" style={{ paddingLeft: 18, margin: 0 }}>
              <li>Microcalcifications <em>suspectes</em> : polymorphes, groupées, linéaires ramifiées.</li>
              <li>Masse : coter forme, marges et densité selon le lexique ACR.</li>
              <li>Densité D ou C : sensibilité mammographique réduite — envisager l'échographie.</li>
              <li>Catégorie 0 : lecture incomplète — comparaison avec examens antérieurs requise.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
