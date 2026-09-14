import { useEffect, useState } from "react";
import { api } from "../../services/api";

interface FusionResult {
  task: string;
  prediction: Record<string, unknown>;
  confiance: number;
  modalites_manquantes: {
    attendues: string[];
    presentes: string[];
    absentes: string[];
    complet: boolean;
    actions: string[];
  };
  modality_importance_pct: Record<string, number>;
  detail: { modalites_encodees: number };
}

interface ModaliteInfo {
  encodeur: string;
  exemples: string[];
}

/** Jeux de données de démonstration par modalité — payloads valides pour les
 * encodeurs NumPy (voir ai/multimodal/core/modality_encoder.py). La modalité
 * tabulaire, elle, utilise le vecteur saisi par l'utilisateur. */
const SAMPLES: Record<string, () => unknown> = {
  imaging_2d: () => ({ tensor: [[0.1, 0.9], [0.4, 0.2]] }),
  imaging_3d: () => ({ tensor: [[0.3, 0.7], [0.8, 0.1]] }),
  signal_1d: () => ({ signal: [1.2, 0.8, 1.5, 0.9, 1.1, 1.4, 0.7, 1.3, 1.0, 0.6, 1.2, 0.9] }),
  texte: () => ({ text: "patient stabilise apres protocole sepsis six" }),
  genomique: () => ({ sequence: "ATGGCGTACCGTTAGCAGAT" }),
  waveform: () => ({ signal: [0.5, 1.1, 0.9, 1.6, 1.2, 0.8, 1.4, 1.0, 0.7, 1.3, 1.1, 0.9] }),
};

/** Scénario par défaut : imagerie 2D + biologie présentes → les 5 autres
 * modalités manquantes (imaging_3d, signal_1d, texte, genomique, waveform)
 * déclenchent l'inférence dégradée ADR-0018 avec confiance recalibrée. */
const DEFAULT_SELECTED = ["imaging_2d", "tabulaire"];

const ALL_MODALITIES = [
  "imaging_2d", "imaging_3d", "signal_1d", "tabulaire",
  "texte", "genomique", "waveform",
];

/** Visionneuse de fusion multimodale : sélection des modalités disponibles,
 * importance par modalité, et bandeau d'inférence dégradée (ADR-0018) —
 * confiance recalibrée + suggestions opérationnelles (runbook PACS…). */
export default function FusionViewer() {
  const [result, setResult] = useState<FusionResult | null>(null);
  const [nominale, setNominale] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [features, setFeatures] = useState("[55, 1, 9.8, 132, 88]");
  const [selected, setSelected] = useState<string[]>(DEFAULT_SELECTED);
  const [registry, setRegistry] = useState<Record<string, ModaliteInfo>>({});
  const [busy, setBusy] = useState(false);

  // Registre des 7 modalités servi par le multimodal-gateway (encodeurs, exemples).
  useEffect(() => {
    api
      .get<{ modalites: Record<string, ModaliteInfo> }>("/api/multimodal/api/v1/modalities")
      .then((r) => setRegistry(r.modalites))
      .catch(() => setRegistry({}));
  }, []);

  function toggle(m: string) {
    setSelected((s) => {
      if (s.includes(m)) return s.length > 1 ? s.filter((x) => x !== m) : s;
      return [...s, m];
    });
  }

  function buildModalities(): Record<string, unknown> | null {
    const out: Record<string, unknown> = {};
    for (const m of selected) {
      if (m === "tabulaire") {
        try {
          out[m] = { features: JSON.parse(features) };
        } catch {
          setError("vecteur tabulaire invalide — ex. [55, 1, 9.8, 132, 88]");
          return null;
        }
      } else {
        out[m] = SAMPLES[m]();
      }
    }
    return out;
  }

  async function run() {
    setError("");
    setNominale(null);
    const modalities = buildModalities();
    if (!modalities) return;
    setBusy(true);
    try {
      const body = { patient_id: "demo", task: "classification", modalities };
      // Inférence réelle (modalités sélectionnées uniquement).
      const main = api.post<FusionResult>("/api/multimodal/api/v1/inference", body);
      // Référence nominale : les 7 modalités présentes — rend le recalibrage
      // ADR-0018 visible (confiance dégradée vs nominale).
      const ref = api
        .post<FusionResult>("/api/multimodal/api/v1/inference", {
          ...body,
          modalities: Object.fromEntries(
            ALL_MODALITIES.map((m) => [
              m,
              m === "tabulaire" ? { features: JSON.parse(features) } : SAMPLES[m](),
            ]),
          ),
        })
        .then((r) => setNominale(r.confiance))
        .catch(() => setNominale(null));
      setResult(await main);
      await ref;
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const absentes = result?.modalites_manquantes.absentes ?? [];
  const degrade = result !== null && absentes.length > 0;

  return (
    <div>
      <h2>Fusion multimodale — cross-attention (ADR-0017/0018)</h2>
      <p className="note">
        Cochez les modalités réellement disponibles au lit du patient : l'inférence
        continue même incomplète, avec une confiance recalibrée (ADR-0018).
      </p>

      <div className="modality-picker">
        {ALL_MODALITIES.map((m) => (
          <label key={m} className={"modality-chip" + (selected.includes(m) ? " on" : "")}>
            <input
              type="checkbox"
              checked={selected.includes(m)}
              onChange={() => toggle(m)}
            />
            <span>
              <strong>{m}</strong>
              {registry[m] && (
                <em> — {registry[m].encodeur}</em>
              )}
            </span>
          </label>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center", margin: "14px 0" }}>
        <input
          value={features}
          onChange={(e) => setFeatures(e.target.value)}
          style={{ width: 340 }}
          aria-label="vecteur tabulaire (biologie)"
        />
        <button onClick={run} disabled={busy}>
          {busy ? "Inférence…" : `Lancer l'inférence (${selected.length}/7 modalités)`}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          {/* Bandeau ADR-0018 : état de complétude + recommandations opérationnelles. */}
          <div className={"banner " + (degrade ? "warn" : "ok")}>
            <h3>
              Modalités manquantes : {absentes.length}
              {degrade && nominale !== null && (
                <span className="conf-delta">
                  {" "}· confiance {(result.confiance * 100).toFixed(0)} %{" "}
                  (nominale {(nominale * 100).toFixed(0)} %)
                </span>
              )}
            </h3>
            <p className="sub">
              {absentes.length
                ? absentes.join(", ")
                : "toutes les modalités attendues sont présentes"}
            </p>
            {result.modalites_manquantes.actions.map((a, i) => (
              <p key={i}>• {a}</p>
            ))}
          </div>

          <div className="cards" style={{ marginTop: 16 }}>
            <div className="card">
              <h3>Prédiction ({result.task})</h3>
              <div className="kpi">{String(Object.values(result.prediction)[0])}</div>
              <div className="sub">
                confiance : {(result.confiance * 100).toFixed(0)} %
                {degrade && " — recalibrée selon les modalités présentes"}
              </div>
              <div className="sub">
                {result.detail?.modalites_encodees ?? selected.length} modalité(s)
                encodée(s) sur 7
              </div>
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
          </div>
        </>
      )}
    </div>
  );
}
