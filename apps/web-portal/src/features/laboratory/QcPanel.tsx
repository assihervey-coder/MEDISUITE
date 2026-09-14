/** Panneau Contrôle qualité (BEST TO HAVE) — règles de Westgard + graphique
 *  Levey-Jennings SVG (zones ±1σ/±2σ/±3σ, points hors contrôle en rouge).
 *  Flux : POST /qc/run → verdict + qc_id → GET /qc/{id}/levey-jennings → points. */
import { useState } from "react";
import { api } from "../../services/api";
import { toast } from "../../store/toastStore";

interface QcVerdict {
  qc_id: string;
  z_scores: number[];
  violations: string[];
  decision: string;
  samples_released: boolean;
}

interface LJPoint {
  value: number;
  z: number;
  zone: string;
  in_control: boolean;
}

/** Analytes du catalogue (REFERENCE_RANGES, clinical-rules lab_qc). */
const ANALYTES = [
  "hemoglobine", "leucocytes", "plaquettes", "creatinine",
  "glucose", "potassium", "sodium", "hba1c", "crp",
];

/** Valeurs de démo par analyte (moyenne cible, écart-type attendu). */
const DEMO: Record<string, { moyenne: number; et: number }> = {
  hemoglobine: { moyenne: 13.5, et: 0.4 },
  leucocytes: { moyenne: 7000, et: 500 },
  plaquettes: { moyenne: 275000, et: 15000 },
  creatinine: { moyenne: 0.95, et: 0.08 },
  glucose: { moyenne: 90, et: 5 },
  potassium: { moyenne: 4.3, et: 0.15 },
  sodium: { moyenne: 140, et: 1.8 },
  hba1c: { moyenne: 5.1, et: 0.2 },
  crp: { moyenne: 2.5, et: 0.5 },
};

/** Graphique Levey-Jennings — SVG pur (aucune dépendance chart). */
function LeveyJenningsChart({ points }: { points: LJPoint[] }) {
  const W = 560, H = 220, PAD = 34;
  const maxAbsZ = Math.max(3.2, ...points.map((p) => Math.abs(p.z)));
  const x = (i: number) => PAD + (i * (W - 2 * PAD)) / Math.max(1, points.length - 1);
  const y = (z: number) => H / 2 - (z / maxAbsZ) * (H / 2 - PAD);

  const zones: Array<{ z: number; color: string; label: string }> = [
    { z: 1, color: "#e5f2e8", label: "±1σ" },
    { z: 2, color: "#f2f7ee", label: "±2σ" },
    { z: 3, color: "#f7f0dd", label: "±3σ" },
  ];

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="lj-chart" role="img"
      aria-label="Graphique Levey-Jennings des contrôles qualité">
      {/* zones symétriques (du plus large au plus étroit) */}
      {[...zones].reverse().map(({ z, color, label }) => (
        <g key={label}>
          <rect x={PAD} y={y(z)} width={W - 2 * PAD} height={y(-z) - y(z)} fill={color} />
          <text x={4} y={y(z) + 4} fontSize="9" fill="#5a7a96">{`+${label}`}</text>
          <text x={4} y={y(-z) - 2} fontSize="9" fill="#5a7a96">{`−${label}`}</text>
        </g>
      ))}
      <line x1={PAD} y1={H / 2} x2={W - PAD} y2={H / 2} stroke="#5a7a96" strokeWidth="1" />
      <text x={4} y={H / 2 + 4} fontSize="9" fill="#5a7a96">moy.</text>

      {/* tracé des z-scores */}
      <polyline
        fill="none" stroke="#2d7ab3" strokeWidth="1.6"
        points={points.map((p, i) => `${x(i)},${y(p.z)}`).join(" ")}
      />
      {points.map((p, i) => (
        <circle key={i} cx={x(i)} cy={y(p.z)} r={p.in_control ? 4 : 5.5}
          fill={p.in_control ? "#2d7ab3" : "#b8604f"}
          stroke={p.in_control ? "none" : "#f7e3de"} strokeWidth="2">
          <title>{`N°${i + 1} — ${p.value} (z=${p.z}, ${p.zone}${p.in_control ? "" : ", HORS CONTRÔLE"})`}</title>
        </circle>
      ))}
      {/* index des points sous l'axe */}
      {points.map((_, i) => (
        <text key={`l${i}`} x={x(i)} y={H - 8} fontSize="9" textAnchor="middle" fill="#5a7a96">
          {i + 1}
        </text>
      ))}
    </svg>
  );
}

export default function QcPanel() {
  const [analyte, setAnalyte] = useState("hemoglobine");
  const [moyenne, setMoyenne] = useState("13.5");
  const [ecartType, setEcartType] = useState("0.4");
  const [valeurs, setValeurs] = useState("13.4, 13.6, 13.5, 14.8, 13.3, 13.6");
  const [verdict, setVerdict] = useState<QcVerdict | null>(null);
  const [points, setPoints] = useState<LJPoint[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function pickAnalyte(a: string) {
    setAnalyte(a);
    const d = DEMO[a];
    if (d) {
      setMoyenne(String(d.moyenne));
      setEcartType(String(d.et));
    }
  }

  async function runQc(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setVerdict(null);
    setPoints([]);
    try {
      const vals = valeurs.split(/[;,\s]+/).map(Number).filter((v) => !Number.isNaN(v));
      if (vals.length < 2) throw new Error("saisissez au moins 2 valeurs de contrôle");
      const res = await api.post<QcVerdict>("/api/lab/api/v1/qc/run", {
        analyte, moyenne: Number(moyenne), ecart_type: Number(ecartType), valeurs: vals,
      });
      setVerdict(res);
      const lj = await api.get<LJPoint[]>(`/api/lab/api/v1/qc/${res.qc_id}/levey-jennings`);
      setPoints(lj);
      if (res.samples_released) {
        toast.ok(`QC accepté (${analyte}) — lots libérés`);
      } else {
        toast.warn(`QC ${res.decision} — ${res.violations.length} violation(s) Westgard, libération bloquée`);
      }
    } catch (err) {
      setError((err as Error).message);
      toast.error(`QC : ${(err as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="qc-panel">
      <h3 style={{ marginTop: 26 }}>Contrôle qualité — règles de Westgard & Levey-Jennings</h3>
      <p className="note">
        ISO 15189 §5.6 : chaque série d'analyses est précédée d'un run QC.
        Violations détectées : 1₂ₛ (avertissement), 1₃ₛ, 2₂ₛ, R₄ₛ, 4₁ₛ, 10x (rejet).
      </p>
      <form onSubmit={runQc} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-end" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: "var(--muted)" }}>
          Analyte
          <select value={analyte} onChange={(e) => pickAnalyte(e.target.value)}>
            {ANALYTES.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: "var(--muted)" }}>
          Moyenne cible
          <input value={moyenne} onChange={(e) => setMoyenne(e.target.value)} required style={{ width: 110 }} inputMode="decimal" />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: "var(--muted)" }}>
          Écart-type
          <input value={ecartType} onChange={(e) => setEcartType(e.target.value)} required style={{ width: 90 }} inputMode="decimal" />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: "var(--muted)", flex: 1, minWidth: 260 }}>
          Valeurs de contrôle (séparées par virgule)
          <input value={valeurs} onChange={(e) => setValeurs(e.target.value)} required />
        </label>
        <button type="submit" disabled={busy}>{busy ? "Analyse…" : "▶ Lancer le run QC"}</button>
      </form>

      {error && <p className="error">{error}</p>}

      {verdict && (
        <div className={`banner ${verdict.samples_released ? "ok" : "warn"}`}>
          <h3>
            Décision : {verdict.decision} —{" "}
            {verdict.samples_released
              ? "✅ lots de samples libérés"
              : "⛔ libération des samples bloquée"}
          </h3>
          <p>
            Violations : {verdict.violations.length === 0
              ? "aucune — série sous contrôle statistique"
              : verdict.violations.map((v) => (
                <span key={v} className="badge critical" style={{ marginRight: 6 }}>
                  {v}
                </span>
              ))}
          </p>
          {points.length > 0 && <LeveyJenningsChart points={points} />}
          <p className="sub">
            Chaque point = un contrôle (z-score vs moyenne cible) · cliquez un point
            pour la valeur · QC n° <code>{verdict.qc_id}</code> conservé en base (traçabilité ISO 15189).
          </p>
        </div>
      )}
    </div>
  );
}
