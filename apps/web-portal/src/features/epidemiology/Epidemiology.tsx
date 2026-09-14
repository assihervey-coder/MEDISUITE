/** Épidémiologie (GOOD TO HAVE) — surveillance santé publique ivoirienne :
 *  paludisme (courbe hebdomadaire + positivité TDR), cascade VIH, activité
 *  événementielle. Sources : analytics-service (aggregation read-only). */
import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { downloadCsv, toCsv } from "../../utils/csv";

interface Palu {
  annee: number;
  semaines: string[];
  cas_suspects: number[];
  tdr_positifs: number[];
  positivite_pct: number;
  tendance: string;
}

interface Vih {
  diagnostiques_pct: number;
  sous_tar_pct: number;
  viro_supprimes_pct: number;
  source: string;
}

interface Activite {
  total: number;
  par_topic: Record<string, number>;
}

/** Barres horizontales (cascade VIH) — SVG pur. */
function Cascade({ rows }: { rows: Array<{ label: string; pct: number; color: string }> }) {
  return (
    <svg viewBox="0 0 420 130" className="epi-chart" role="img" aria-label="Cascade de soins VIH">
      {rows.map((r, i) => (
        <g key={r.label}>
          <rect x={110} y={12 + i * 38} width={Math.max(4, (r.pct / 100) * 270)} height={22}
            rx={5} fill={r.color} />
          <text x={104} y={27 + i * 38} fontSize="11.5" textAnchor="end" fill="#142840">
            {r.label}
          </text>
          <text x={114 + Math.max(4, (r.pct / 100) * 270)} y={27 + i * 38} fontSize="12"
            fontWeight="700" fill="#142840">
            {r.pct} %
          </text>
        </g>
      ))}
    </svg>
  );
}

export default function Epidemiology() {
  const [palu, setPalu] = useState<Palu | null>(null);
  const [vih, setVih] = useState<Vih | null>(null);
  const [act, setAct] = useState<Activite | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.get<Palu>("/api/analytics/api/v1/epidemiologie/paludisme"),
      api.get<Vih>("/api/analytics/api/v1/epidemiologie/vih"),
      api.get<Activite>("/api/analytics/api/v1/activite"),
    ])
      .then(([p, v, a]) => { setPalu(p); setVih(v); setAct(a); })
      .catch((e) => setError(e.message));
  }, []);

  function exportPalu() {
    if (!palu) return;
    downloadCsv(
      "epidemiologie-paludisme.csv",
      toCsv(
        palu.semaines.map((s, i) => ({
          semaine: s,
          cas_suspects: palu.cas_suspects[i],
          tdr_positifs: palu.tdr_positifs[i],
        })),
        ["semaine", "cas_suspects", "tdr_positifs"],
      ),
    );
  }

  if (error) return <div><h2>Épidémiologie</h2><p className="error">analytics-service injoignable : {error}</p></div>;
  if (!palu || !vih || !act) return <p className="note">Chargement des indicateurs…</p>;

  const maxSuspects = Math.max(...palu.cas_suspects);
  const W = 640, H = 220, PAD = 40;
  const bw = (W - 2 * PAD) / palu.semaines.length;
  const ySus = (v: number) => H - 34 - (v / maxSuspects) * (H - 74);

  return (
    <div>
      <h2>Épidémiologie — surveillance santé publique 🇨🇮</h2>

      <div className="detail-grid">
        <div className="card">
          <h3>Paludisme — semaine {palu.annee} (12 dernières semaines)</h3>
          <svg viewBox={`0 0 ${W} ${H}`} className="epi-chart" role="img"
            aria-label={`Cas suspects de paludisme, positivité TDR ${palu.positivite_pct} %`}>
            {palu.semaines.map((s, i) => {
              const suspects = palu.cas_suspects[i];
              const pos = palu.tdr_positifs[i];
              return (
                <g key={s}>
                  <rect x={PAD + i * bw + 2} y={ySus(suspects)} width={bw - 6}
                    height={H - 34 - ySus(suspects)} rx={3} fill="#2d7ab3">
                    <title>{`${s} : ${suspects} suspects, ${pos} TDR+`}</title>
                  </rect>
                  <rect x={PAD + i * bw + bw / 2 - 1} y={ySus(pos)} width={Math.max(4, bw * 0.55)}
                    height={H - 34 - ySus(pos)} rx={2} fill="#c9a54a">
                    <title>{`${s} : ${pos} TDR+`}</title>
                  </rect>
                  <text x={PAD + i * bw + bw / 2} y={H - 20} fontSize="9" textAnchor="middle" fill="#5a7a96">
                    {s}
                  </text>
                </g>
              );
            })}
          </svg>
          <p className="sub">
            <span className="legend-dot" style={{ background: "#2d7ab3" }} /> cas suspects ·
            <span className="legend-dot" style={{ background: "#c9a54a" }} /> TDR positifs ·
            positivité globale : <strong>{palu.positivite_pct} %</strong>
          </p>
          <p className="note">📈 {palu.tendance}</p>
          <button type="button" onClick={exportPalu}>⬇ Export CSV (PNLP)</button>
        </div>

        <div className="card">
          <h3>VIH — cascade de soins (ONUSIDA 90-90-90)</h3>
          <Cascade
            rows={[
              { label: "diagnostiqués", pct: vih.diagnostiques_pct, color: "#2d7ab3" },
              { label: "sous TAR", pct: vih.sous_tar_pct, color: "#6a9a7a" },
              { label: "suppression virale", pct: vih.viro_supprimes_pct, color: "#c9a54a" },
            ]}
          />
          <p className="note">{vih.source}</p>
          <h3 style={{ marginTop: 14 }}>Activité de la plateforme (7 j)</h3>
          <p style={{ fontSize: 13 }}>
            {Object.entries(act.par_topic).map(([topic, n]) => (
              <span key={topic} style={{ marginRight: 12 }}>
                <code style={{ fontSize: 11.5 }}>{topic}</code> : <strong>{n}</strong>
              </span>
            ))}
          </p>
          <p className="note">Total : {act.total} événements traités par le bus d'intégration.</p>
        </div>
      </div>

      <p className="note" style={{ marginTop: 14 }}>
        Indicateurs agrégés en lecture seule (database-per-service) — aucune donnée
        nominative. Branchement DHIS2 prévu en production (interopérabilité FHIR/ADX).
      </p>
    </div>
  );
}
