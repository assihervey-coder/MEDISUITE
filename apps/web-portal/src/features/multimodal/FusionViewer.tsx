import { useState } from "react";
import { api } from "../../services/api";

interface FusionResult {
  task: string;
  prediction: Record<string, unknown>;
  confiance: number;
  modalites_manquantes: { absentes: string[]; actions: string[] };
  modality_importance_pct: Record<string, number>;
}

/** Visionneuse de fusion multimodale : importance des modalités + modalités manquantes. */
export default function FusionViewer() {
  const [result, setResult] = useState<FusionResult | null>(null);
  const [error, setError] = useState("");
  const [features, setFeatures] = useState("[55, 1, 9.8, 132, 88]");

  async function run(withImaging: boolean) {
    setError("");
    try {
      const modalities: Record<string, unknown> = {
        tabulaire: { features: JSON.parse(features) },
      };
      if (withImaging) {
        modalities.imaging_2d = { tensor: [[0.1, 0.9], [0.4, 0.2]] };
      }
      setResult(
        await api.post<FusionResult>("/api/multimodal/api/v1/inference", {
          patient_id: "demo",
          task: "classification",
          modalities,
        })
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div>
      <h2>Fusion multimodale — cross-attention (ADR-0017/0018)</h2>
      <p className="note">
        Résilience aux modalités manquantes : retirez l'imagerie, l'inférence continue
        avec une confiance recalibrée.
      </p>
      <div style={{ display: "flex", gap: 8, alignItems: "center", margin: "14px 0" }}>
        <input value={features} onChange={(e) => setFeatures(e.target.value)} style={{ width: 340 }} />
        <button onClick={() => run(true)}>Inférence complète</button>
        <button onClick={() => run(false)}>Sans imagerie (dégradé)</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="cards">
          <div className="card">
            <h3>Prédiction ({result.task})</h3>
            <div className="kpi">{String(Object.values(result.prediction)[0])}</div>
            <div className="sub">confiance : {(result.confiance * 100).toFixed(0)} %</div>
          </div>
          <div className="card">
            <h3>Importance des modalités</h3>
            {Object.entries(result.modality_importance_pct).map(([m, pct]) => (
              <p key={m} style={{ margin: "4px 0" }}>
                <strong>{m}</strong> — {pct} %
                <span
                  style={{
                    display: "inline-block", height: 8, marginLeft: 8,
                    width: `${pct * 2}px`, background: "var(--accent)", borderRadius: 4,
                  }}
                />
              </p>
            ))}
          </div>
          <div className="card">
            <h3>Modalités manquantes : {result.modalites_manquantes.absentes.length}</h3>
            <p className="sub">{result.modalites_manquantes.absentes.join(", ") || "aucune"}</p>
            {result.modalites_manquantes.actions.map((a, i) => (
              <p key={i} className="note">• {a}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
