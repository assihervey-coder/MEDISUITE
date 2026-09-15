/** Épidémiologie (GOOD TO HAVE) — surveillance santé publique ivoirienne :
 *  paludisme (courbe hebdomadaire + positivité TDR), cascade VIH, activité
 *  événementielle, carte des éclosions TropiRAG (14 districts, comptes
 *  déterministes), export DHIS2 (file offline / push serveur MSP-CI).
 *  Sources : analytics-service + tropirag-service. */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../services/api";
import { downloadCsv, toCsv } from "../../utils/csv";
import {
  buildMapTiles, nationalChips, outbreakLines, type TrSurveillance,
} from "./outbreaks";
import {
  cronLabel, currentIsoWeek, dhis2ModeLabel, dhis2QueueLine, exportSummaryRows,
  lastRunLabel, payloadStats, type Dhis2CronStatus, type Dhis2ExportResult,
  type Dhis2PushResult, type Dhis2Status,
} from "./dhis2";

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
  const [surv, setSurv] = useState<TrSurveillance | null>(null);
  const [survErr, setSurvErr] = useState("");
  const [error, setError] = useState("");
  // --- DHIS2 (export hebdo branché sur la surveillance TropiRAG) ---------
  const [dhis2, setDhis2] = useState<Dhis2Status | null>(null);
  const [dhis2Cron, setDhis2Cron] = useState<Dhis2CronStatus | null>(null);
  const [dhis2Export, setDhis2Export] = useState<Dhis2ExportResult | null>(null);
  const [dhis2Msg, setDhis2Msg] = useState("");
  const [dhis2Busy, setDhis2Busy] = useState(false);
  const [dhis2Week, setDhis2Week] = useState(() => currentIsoWeek());

  useEffect(() => {
    Promise.all([
      api.get<Palu>("/api/analytics/api/v1/epidemiologie/paludisme"),
      api.get<Vih>("/api/analytics/api/v1/epidemiologie/vih"),
      api.get<Activite>("/api/analytics/api/v1/activite"),
    ])
      .then(([p, v, a]) => { setPalu(p); setVih(v); setAct(a); })
      .catch((e) => setError(e.message));
    // Surveillance éclosions TropiRAG : échec en mode dégradé — n'affecte
    // pas les indicateurs analytics (disponibilité indépendante des services).
    api.get<TrSurveillance>("/api/tropirag/api/v1/surveillance/map?days=30")
      .then(setSurv)
      .catch((e) => setSurvErr((e as Error).message));
    // Statut DHIS2 : échec fail-soft (le panneau se masque simplement).
    api.get<Dhis2Status>("/api/tropirag/api/v1/export/dhis2/status")
      .then(setDhis2)
      .catch(() => setDhis2(null));
    // Cron hebdo MSP-CI : échec fail-soft (ligne absente si tropirag down).
    api.get<Dhis2CronStatus>("/api/tropirag/api/v1/export/dhis2/cron")
      .then(setDhis2Cron)
      .catch(() => setDhis2Cron(null));
  }, []);

  async function refreshDhis2() {
    try { setDhis2(await api.get<Dhis2Status>("/api/tropirag/api/v1/export/dhis2/status")); }
    catch { /* statut seul — l'export reste affiché */ }
  }

  async function exportDhis2() {
    setDhis2Busy(true); setDhis2Msg("");
    try {
      const r = await api.post<Dhis2ExportResult>("/api/tropirag/api/v1/export/dhis2",
        { period: dhis2Week, format: "json", enqueue: true });
      setDhis2Export(r);
      setDhis2Msg(r.notes.join(" · ") || `export ${r.period} : ${r.data_values.length} valeurs`);
      await refreshDhis2();
    } catch (e) { setDhis2Msg(`échec export : ${(e as Error).message}`); }
    finally { setDhis2Busy(false); }
  }

  async function pushDhis2() {
    setDhis2Busy(true); setDhis2Msg("");
    try {
      const r = await api.post<Dhis2PushResult>("/api/tropirag/api/v1/export/dhis2/push");
      if (typeof r.pushed === "number") {
        setDhis2Msg(`push : ${r.pushed} envoyé(s), ${r.failed ?? 0} échec(s)`);
      } else {
        setDhis2Msg(r.detail || "aucun payload en attente");
      }
      await refreshDhis2();
    } catch (e) { setDhis2Msg(`échec push : ${(e as Error).message}`); }
    finally { setDhis2Busy(false); }
  }

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

      {survErr && (
        <p className="note" style={{ marginTop: 14 }}>
          Surveillance TropiRAG indisponible (tropirag-service injoignable) : {survErr}
        </p>
      )}

      {surv && (
        <div className="card" style={{ marginTop: 14 }} data-testid="epi-outbreaks">
          <h3>⚠ Surveillance des éclosions — TropiRAG (14 districts sanitaires, {surv.window_days} j)</h3>
          <p className="note">
            Agrégation <strong>100 % déterministe</strong> des analyses TropiRAG par district de
            voyage (aucune IA dans le comptage — même source de vérité que l'export DHIS2).
            Signal = progression de la dernière semaine vs précédente (+2 cas, seuil ≥ 3).
          </p>

          {surv.outbreaks.length > 0 ? (
            <div className="banner warn" role="alert">
              <strong>Signaux d'éclosion actifs :</strong>
              <ul style={{ margin: "6px 0 0 18px" }} data-testid="epi-outbreak-list">
                {outbreakLines(surv).map((l) => <li key={l}>{l}</li>)}
              </ul>
            </div>
          ) : (
            <p className="note">✓ Aucun signal d'éclosion sur la fenêtre ({surv.total_cases} cas analysés).</p>
          )}

          <div className="epi-outbreak-map" style={{ marginTop: 12 }}>
            {buildMapTiles(surv).map((t) => (
              <div key={t.key}
                className={`epi-tile ${t.outbreak ? "outbreak" : ""}`}
                style={{
                  gridColumn: t.col, gridRow: t.row,
                  background: t.tone,
                  border: t.outbreak ? "2px solid #b3402f" : "1px solid var(--border, rgba(127,127,127,.25))",
                }}
                title={t.title}
                data-testid={`epi-district-${t.key}${t.outbreak ? " outbreak" : ""}`}
              >
                <span className="epi-tile-town">{t.chief_town}</span>
                <span className="epi-tile-cases">{t.outbreak ? "⚠ " : ""}{t.cases} cas</span>
              </div>
            ))}
          </div>

          <p style={{ marginTop: 10 }}>
            {nationalChips(surv).map((c) => (
              <span key={c.label} className="modality-chip on" style={{ cursor: "default", marginRight: 6 }}>
                {c.label} : <strong>{c.n}</strong>
              </span>
            ))}
            {surv.non_localises.cases > 0 && (
              <span className="modality-chip" style={{ cursor: "default" }}>
                non localisés : <strong>{surv.non_localises.cases}</strong>
              </span>
            )}
          </p>

          <p className="note" style={{ marginTop: 8 }}>
            <Link to="/decision">🧭 Analyser un cas fièvre + voyage</Link> — chaque analyse alimente
            la surveillance (district résolu depuis le segment CI du voyage).
          </p>
        </div>
      )}

      {dhis2 && (
        <div className="card" style={{ marginTop: 14 }} data-testid="epi-dhis2">
          <h3>🏛 Export DHIS2 — surveillance hebdomadaire (MSP-CI)</h3>
          <p className="note">
            <strong>{dhis2ModeLabel(dhis2)}</strong> — indicateurs agrégés
            ({dhis2.config.elements_mapped} éléments mappés, org unit
            <code style={{ marginLeft: 4 }}>{dhis2.config.org_unit}</code>),
            format dataValueSets JSON / ADX 2.0. {dhis2QueueLine(dhis2)}.
          </p>
          <p style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <label htmlFor="dhis2-week" style={{ fontSize: 13 }}>Semaine ISO :</label>
            <input id="dhis2-week" value={dhis2Week} data-testid="epi-dhis2-week"
              onChange={(e) => setDhis2Week(e.target.value.toUpperCase().trim())}
              placeholder="2026W38" size={9}
              style={{ padding: "4px 6px" }} />
            <button type="button" onClick={exportDhis2} disabled={dhis2Busy}
              data-testid="epi-dhis2-export">⬆ Exporter la semaine</button>
            <button type="button" onClick={pushDhis2} disabled={dhis2Busy}
              data-testid="epi-dhis2-push">🚀 Pousser la file vers DHIS2</button>
          </p>
          {dhis2Msg && (
            <p className="note" data-testid="epi-dhis2-msg">{dhis2Msg}</p>
          )}
          {dhis2Export && (
            <>
              <p style={{ margin: "8px 0 4px" }}>
                <strong>{dhis2Export.rows_analyzed}</strong> analyses agrégées pour
                <strong> {dhis2Export.period}</strong> :
                {exportSummaryRows(dhis2Export).map((r) => (
                  <span key={r.key} className="modality-chip on"
                    style={{ cursor: "default", marginLeft: 6 }}>
                    {r.label} : <strong>{r.value}</strong>
                  </span>
                ))}
                {exportSummaryRows(dhis2Export).length === 0 && (
                  <span className="note"> aucune valeur &gt; 0 sur la période</span>
                )}
              </p>
              <details>
                <summary>Payload dataValueSets ({payloadStats(dhis2Export.payload).values} valeurs)</summary>
                <pre data-testid="epi-dhis2-payload"
                  style={{ fontSize: 11.5, maxHeight: 240, overflow: "auto" }}>
                  {dhis2Export.payload}
                </pre>
              </details>
            </>
          )}
          {dhis2Cron && (
            <p className="note" data-testid="epi-dhis2-cron">
              🕒 {cronLabel(dhis2Cron)}
              {dhis2Cron.next_run ? ` — prochain : ${dhis2Cron.next_run.slice(0, 16).replace("T", " ")}` : ""}
              <br />{lastRunLabel(dhis2Cron)}
            </p>
          )}
          <p className="note" style={{ marginTop: 8 }}>
            Défaut <strong>offline_queue</strong> : aucun envoi réseau implicite.
            Push serveur MSP-CI réel via <code>TROPIRAG_DHIS2_BASE_URL</code> +
            <code>TROPIRAG_DHIS2_USERNAME</code> + <code>TROPIRAG_DHIS2_PASSWORD</code>
            (mode <code>push</code>) — UIDs à confirmer avec le dictionnaire de
            données national (validateur <code>scripts/validate_dhis2_uids.py</code>).
          </p>
        </div>
      )}

      <p className="note" style={{ marginTop: 14 }}>
        Indicateurs agrégés en lecture seule (database-per-service) — aucune donnée
        nominative. Export DHIS2 branché sur la surveillance TropiRAG (comptes
        déterministes, même source de vérité que le cartographe d'éclosions).
      </p>
    </div>
  );
}
