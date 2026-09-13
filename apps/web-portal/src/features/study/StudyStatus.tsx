/**
 * Écran promoteur « Study Status / Lock » — investigation MEDISUITE-CI-01
 * (v0.9, pilotage R6→R7).
 *
 * Cockpit de pilotage du promoteur, appuyé sur les endpoints eCRF existants
 * (aucune modification backend) :
 * - GET /study/status  (ecrf.read)  → verrou de base M+18, compteurs ;
 * - GET /exports/dsmb  (ecrf.export) → agrégats sans PHI (sûreté, délais) ;
 * - GET /forms         (ecrf.read)  → identité étude + sites ;
 * - POST /study/lock   (ecrf.lock)  → verrouillage irréversible M+18,
 *   action du PROMOTEUR uniquement (RBAC fail-closed côté serveur), arme
 *   une confirmation typée « VERROU MEDISUITE-CI-01 » + 2 témoins.
 *
 * Honnêteté réglementaire : la validité clinique des sorties IA reste 🔴
 * jusqu'à R6-R8 — cet écran pilote l'INSTRUMENT de mesure, pas un verdict.
 */
import { useCallback, useEffect, useState, type CSSProperties } from "react";
import { api, ApiError } from "../../services/api";
import { useAuth } from "../../store/authStore";
import { useOfflineStore } from "../../offline/offlineStore";
import {
  activePhase,
  formatChecksum,
  lockPayload,
  lockReadiness,
  siteLabel,
  TIMELINE,
  type LockForm,
} from "./status-logic";

const BASE = "/api/ecrf/api/v1/ecrf";

interface StatusResp {
  study: string;
  locked: boolean;
  locked_at?: number | null;
  locked_by?: string | null;
  temoins?: string[];
  checksum?: string | null;
  checksum_courant?: string | null;
  note?: string;
  sujets: number;
  entrees_signees: number;
  requetes_ouvertes: number;
}

interface DsmbResp {
  study: string;
  sujets: { total: number; par_site: Record<string, number>; par_scenario: Record<string, number>; par_statut: Record<string, number> };
  entrees: { total: number; par_formulaire: Record<string, number> };
  surete: { EI_lies_dispositif: number; SAE_lies_dispositif: number; regle_arret: string };
  p3_delai_orientation_min: { n: number; mediane: number | null };
  adhesion: Record<string, number>;
}

interface Catalogue {
  study: string;
  version: string;
  sites: Record<string, string>;
  scenarios: Record<string, string>;
}

const EMPTY_STATUS: StatusResp = {
  study: "MEDISUITE-CI-01",
  locked: false,
  sujets: 0,
  entrees_signees: 0,
  requetes_ouvertes: 0,
};

const cardStyle: CSSProperties = { marginTop: 18 };
const grid2: CSSProperties = { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 };

export default function StudyStatus() {
  const { role } = useAuth();
  const { online } = useOfflineStore();
  const [status, setStatus] = useState<StatusResp>(EMPTY_STATUS);
  const [dsmb, setDsmb] = useState<DsmbResp | null>(null);
  const [cat, setCat] = useState<Catalogue | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showLock, setShowLock] = useState(false);
  const [lockForm, setLockForm] = useState<LockForm>({
    temoin1: "",
    temoin2: "",
    declaration: "",
    confirmation: "",
  });

  const reload = useCallback(async () => {
    setError("");
    try {
      const [s, c] = await Promise.all([
        api.get<StatusResp>(`${BASE}/study/status`),
        api.get<Catalogue>(`${BASE}/forms`),
      ]);
      setStatus(s);
      setCat(c);
      try {
        setDsmb(await api.get<DsmbResp>(`${BASE}/exports/dsmb`));
      } catch {
        setDsmb(null); // ecrf.export requis — écran consultable sans l'agrégat
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError("Accès refusé (RBAC fail-closed) — permission ecrf.read requise.");
      } else {
        setError(
          "Pilotage indisponible : " +
            (err instanceof Error ? err.message : String(err)) +
            " — cet écran est une lecture réseau vivante, rien n'est mis en cache.",
        );
      }
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const doLock = async () => {
    const check = lockPayload(lockForm, status.study);
    if (!check.ok || !check.body) {
      setError(check.errors.join(" · "));
      return;
    }
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await api.post(`${BASE}/study/lock`, check.body);
      setShowLock(false);
      setLockForm({ temoin1: "", temoin2: "", declaration: "", confirmation: "" });
      setMessage(
        "Verrou de base POSÉ (irréversible) — l'extraction d'analyse est débloquée pour le data manager ; journalisation ecrf.study.lock + événement bus.",
      );
      await reload();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError(`Verrouillage refusé : ${err.message}`);
      } else if (err instanceof ApiError && err.status === 403) {
        setError("Réservé au promoteur (ecrf.lock) — RBAC fail-closed.");
      } else {
        setError(`Erreur : ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setBusy(false);
    }
  };

  const readiness = lockReadiness(status);
  const phase = activePhase(status);
  const isPromoteur = role === "promoteur";

  return (
    <div>
      <h2>📈 Promoteur — {status.study} {cat ? `(protocole v${cat.version})` : ""}</h2>
      <p className="sub">
        Pilotage de l'investigation multicentrique (MDR Annexe XV / ISO 14155) —
        phase active&nbsp;
        <span className="badge ok">{phase}</span> · validité clinique des sorties IA&nbsp;
        <span className="badge critical">🔴 jusqu'à R6-R8</span>
      </p>

      {!online && (
        <p className="badge warn" style={{ display: "inline-block", marginTop: 8 }}>
          Hors connexion — ce cockpit lit des indicateurs vivants, aucune donnée
          n'est servie depuis le cache : reconnectez-vous.
        </p>
      )}
      {error && <p className="error">{error}</p>}
      {message && <p style={{ color: "var(--ok)", fontSize: 13 }}>{message}</p>}

      {/* ── Timeline R5→R8 ─────────────────────────────────────────── */}
      <div className="card" style={cardStyle}>
        <h3>Plan de validation v1.0.0 — fenêtres d'investigation</h3>
        <table>
          <thead>
            <tr>
              <th>Jalon</th>
              <th>Fenêtre</th>
              <th>Titre</th>
              <th>Contenu</th>
              <th>État</th>
            </tr>
          </thead>
          <tbody>
            {TIMELINE.map((t) => {
              const active = t.jalon === phase;
              return (
                <tr key={t.jalon}>
                  <td>
                    <strong>{t.jalon}</strong>
                  </td>
                  <td>
                    M+{t.from} → {t.to === 31 ? "M+30+" : `M+${t.to}`}
                  </td>
                  <td>{t.titre}</td>
                  <td style={{ fontSize: 12.5 }}>{t.detail}</td>
                  <td>
                    {active ? (
                      <span className="badge ok">phase active</span>
                    ) : t.jalon === "R5" ? (
                      <span className="badge warn">soumissions 🔴 terrain</span>
                    ) : (
                      <span className="badge">à venir</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* ── Verrou de base M+18 ─────────────────────────────────────── */}
      <div className="card" style={cardStyle}>
        <h3>Verrou de base (lock M+18) — protocole §7.4</h3>
        <div className="cards">
          <div className="card">
            <div className="sub">État du verrou</div>
            <div className="kpi">{status.locked ? "🔒 POSÉ" : "🔓 OUVERT"}</div>
            <div className="sub">
              {status.locked
                ? `le ${status.locked_at ? new Date(status.locked_at * 1000).toLocaleString("fr-FR") : "—"} par ${status.locked_by ?? "—"}`
                : status.checksum_courant
                  ? `checksum courant (indicatif) : ${formatChecksum(status.checksum_courant)}`
                  : status.note ?? ""}
            </div>
          </div>
          <div className="card">
            <div className="sub">Sujets inclus</div>
            <div className="kpi">{status.sujets}</div>
            <div className="sub">{status.entrees_signees} entrée(s) signée(s)</div>
          </div>
          <div className="card">
            <div className="sub">Requêtes SDV ouvertes</div>
            <div className="kpi">{status.requetes_ouvertes}</div>
            <div className="sub">
              {status.requetes_ouvertes === 0
                ? "aucune — condition de lock respectée"
                : "clôture requise avant le verrou (plan-monitoring §5)"}
            </div>
          </div>
          <div className="card">
            <div className="sub">Témoins du verrou</div>
            <div className="kpi" style={{ fontSize: 18 }}>
              {status.locked ? (status.temoins?.length ?? 0) : "—"}
            </div>
            <div className="sub">
              {status.locked
                ? (status.temoins ?? []).join(", ") || "—"
                : "≥ 2 témoins requis au moment du lock"}
            </div>
          </div>
        </div>

        {status.locked ? (
          <p style={{ marginTop: 12, fontSize: 13 }}>
            <span className="badge ok">extraction SAF débloquée</span> — GET
            /api/v1/ecrf/extract (data manager uniquement, alarme d'intégrité si
            divergence du checksum {formatChecksum(status.checksum)}).
          </p>
        ) : isPromoteur ? (
          <>
            {showLock ? (
              <div style={{ marginTop: 12 }}>
                <p className="error">
                  ⚠️ Opération IRRÉVERSIBLE : après le verrou, toute écriture
                  eCRF est refusée (409) et aucun déverrouillage n'existe — un
                  correctif passe par un amendement documenté (EGSP).
                </p>
                <div style={grid2}>
                  <input
                    placeholder="Témoin 1 (nom complet)"
                    value={lockForm.temoin1}
                    onChange={(e) => setLockForm({ ...lockForm, temoin1: e.target.value })}
                  />
                  <input
                    placeholder="Témoin 2 (nom complet)"
                    value={lockForm.temoin2}
                    onChange={(e) => setLockForm({ ...lockForm, temoin2: e.target.value })}
                  />
                </div>
                <input
                  style={{ marginTop: 8, width: "100%", boxSizing: "border-box" }}
                  placeholder="Déclaration (optionnelle, ≤ 500 caractères)"
                  value={lockForm.declaration}
                  onChange={(e) => setLockForm({ ...lockForm, declaration: e.target.value })}
                />
                <input
                  style={{ marginTop: 8, width: "100%", boxSizing: "border-box" }}
                  placeholder={`Taper « VERROU ${status.study} » pour confirmer`}
                  value={lockForm.confirmation}
                  onChange={(e) => setLockForm({ ...lockForm, confirmation: e.target.value })}
                />
                <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
                  <button disabled={busy} onClick={doLock}>
                    🔒 Poser le verrou M+18
                  </button>
                  <button onClick={() => setShowLock(false)} disabled={busy}>
                    Annuler
                  </button>
                </div>
                {!readiness.ready && (
                  <p className="error" style={{ marginTop: 8 }}>
                    Préconditions non réunies : {readiness.blocages.join(" · ")}
                  </p>
                )}
              </div>
            ) : (
              <div style={{ marginTop: 12 }}>
                <button onClick={() => setShowLock(true)}>
                  Ouvrir le protocole de verrouillage…
                </button>
                {!readiness.ready && (
                  <p className="error" style={{ marginTop: 8 }}>
                    Préconditions non réunies : {readiness.blocages.join(" · ")}
                  </p>
                )}
              </div>
            )}
          </>
        ) : (
          <p className="sub" style={{ marginTop: 12 }}>
            L'action de verrouillage est réservée au rôle promoteur
            (ecrf.lock) — consultation en lecture seule pour « {role || "anonyme"} ».
          </p>
        )}
      </div>

      {/* ── Agrégats DSMB (sans PHI) ───────────────────────────────── */}
      <div className="card" style={cardStyle}>
        <h3>Agrégats DSMB (export sans PHI, §6 du protocole)</h3>
        {!dsmb ? (
          <p className="sub">
            Agrégats indisponibles (permission ecrf.export requise ou service
            injoignable) — le promoteur en dispose via son rôle dédié.
          </p>
        ) : (
          <>
            <div style={grid2}>
              <div>
                <h4 style={{ margin: "6px 0" }}>Sujets par site</h4>
                <table>
                  <tbody>
                    {Object.entries(dsmb.sujets.par_site).length === 0 ? (
                      <tr>
                        <td className="sub">aucune inclusion à ce jour</td>
                      </tr>
                    ) : (
                      Object.entries(dsmb.sujets.par_site).map(([s, n]) => (
                        <tr key={s}>
                          <td>{siteLabel(cat?.sites, s)}</td>
                          <td>{n}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <div>
                <h4 style={{ margin: "6px 0" }}>Sujets par scénario</h4>
                <table>
                  <tbody>
                    {Object.entries(dsmb.sujets.par_scenario).length === 0 ? (
                      <tr>
                        <td className="sub">aucune inclusion à ce jour</td>
                      </tr>
                    ) : (
                      Object.entries(dsmb.sujets.par_scenario).map(([s, n]) => (
                        <tr key={s}>
                          <td>
                            {s} — {cat?.scenarios?.[s] ?? "scénario inconnu"}
                          </td>
                          <td>{n}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
            <p style={{ fontSize: 13, marginTop: 10 }}>
              Sûreté : {dsmb.surete.EI_lies_dispositif} EI / {dsmb.surete.SAE_lies_dispositif}{" "}
              SAE liés au dispositif — règle d'arrêt : {dsmb.surete.regle_arret}. Délai
              d'orientation P3 : médiane{" "}
              {dsmb.p3_delai_orientation_min.mediane !== null
                ? `${dsmb.p3_delai_orientation_min.mediane} min (n=${dsmb.p3_delai_orientation_min.n})`
                : "non calculable (n=0)"}
              .
            </p>
          </>
        )}
      </div>

      {/* ── Références réglementaires ──────────────────────────────── */}
      <div className="card" style={cardStyle}>
        <h3>Références du dossier d'investigation</h3>
        <ul style={{ fontSize: 13, lineHeight: 1.7 }}>
          <li>Protocole TD-10 (v1.0-draft) — <code>compliance/mdr/technical-documentation/10-protocole-investigation-multicentrique-R5.md</code></li>
          <li>Kit de signatures terrain R5 — <code>compliance/mdr/clinical/signatures/</code> (page de signatures, registre investigateurs, journal de délégation)</li>
          <li>Soumissions ANOC-CI / PACTR / Ministère — <code>compliance/mdr/submissions/00-index-soumissions.md</code></li>
          <li>Plan de monitoring + rapports de visite A4 — <code>compliance/mdr/clinical/monitoring/</code></li>
          <li>Rapport clinique MEDDEV 2.7/1 (R7, ADR-0026) — <code>compliance/mdr/technical-documentation/11-rapport-evaluation-clinique-meddev-271.md</code></li>
        </ul>
      </div>
    </div>
  );
}
