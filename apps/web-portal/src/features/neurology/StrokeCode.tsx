/**
 * Code AVC — parcours urgentiel stroke (module 13 · Neurologie).
 * Écran spécialisé : horloge « dernier vu normal » (LKW) avec fenêtres
 * thérapeutiques, cotation NIHSS 11 items simplifiés, ASPECTS 10 régions,
 * checklist de contre-indications à la thrombolyse, synthèse d'aide à la
 * décision. Les scores sont calculés par packages/clinical-rules via
 * neurology-service (POST /api/v1/scores/nihss et /scores/aspects).
 * Référentiels : NIHSS (Lyden 2001), ASPECTS (Barber, Lancet 2000),
 * fenêtres AHA/ASA (alteplase ≤ 4,5 h ; thrombectomie ≤ 6 h, 6-24 h avec
 * imagerie de perfusion DAWN/DEFUSE-3).
 */
import { useEffect, useMemo, useState } from "react";
import { postScore } from "../../services/api";

interface NihssResult { score: number; gravite: string; thrombolyse_candidate: boolean }
interface AspectsResult { score: number; thrombectomie_candidate: boolean; interpretation: string }

/** 13 clés NIHSS attendues par medisuite_rules.neurology.nihss, avec bornes réalistes (total 0-38). */
const NIHSS_ITEMS: Array<{ key: string; label: string; max: number }> = [
  { key: "niveau_conscience", label: "Niveau de conscience", max: 3 },
  { key: "regard", label: "Regard", max: 2 },
  { key: "champ_visuel", label: "Champ visuel", max: 3 },
  { key: "facial", label: "Paralysie faciale", max: 3 },
  { key: "moteur_bras_g", label: "Moteur bras gauche", max: 4 },
  { key: "moteur_bras_d", label: "Moteur bras droit", max: 4 },
  { key: "moteur_jambe_g", label: "Moteur jambe gauche", max: 4 },
  { key: "moteur_jambe_d", label: "Moteur jambe droit", max: 4 },
  { key: "ataxie", label: "Ataxie cérébelleuse", max: 2 },
  { key: "sensoriel", label: "Sensoriel", max: 2 },
  { key: "langage", label: "Langage (aphasie)", max: 3 },
  { key: "dysarthrie", label: "Dysarthrie", max: 2 },
  { key: "extinction", label: "Extinction / inattention", max: 2 },
];

/** 10 régions ASPECTS — 1 = saine, 0 = signe d'ischémie précoce. */
const ASPECTS_REGIONS: Array<{ key: string; label: string }> = [
  { key: "caudate", label: "Noyau caudé" },
  { key: "lenticular", label: "Noyau lenticulaire" },
  { key: "internal_capsule", label: "Capsule interne" },
  { key: "insula", label: "Insula" },
  { key: "M1", label: "M1" }, { key: "M2", label: "M2" }, { key: "M3", label: "M3" },
  { key: "M4", label: "M4" }, { key: "M5", label: "M5" }, { key: "M6", label: "M6" },
];

const CONTRAINDICATIONS: string[] = [
  "INR > 1,7 ou anticoagulant oral en cours",
  "Plaquettes < 100 G/L",
  "PA > 185/110 mmHg non contrôlée",
  "Chirurgie majeure ou AVC récent < 3 mois",
  "Hémorragie active ou diathèse hémorragique",
  "Glycémie < 0,50 g/L",
  "Hémorragie intracrânienne connue (TDM)",
  "Grossesse (cas discutés)",
];

const FENETRE_ALTEPLASE = 270; // minutes (4,5 h)
const FENETRE_THROMBECTOMIE = 360; // minutes (6 h)

function bandOf(elapsed: number | null): { label: string; cls: string } {
  if (elapsed === null) return { label: "— renseignez l'heure LKW —", cls: "" };
  if (elapsed < 0) return { label: "horloge LKW dans le futur ? vérifier", cls: "stop" };
  if (elapsed <= FENETRE_ALTEPLASE) return { label: "Fenêtre alteplase ouverte (≤ 4,5 h)", cls: "go" };
  if (elapsed <= FENETRE_THROMBECTOMIE) return { label: "Fenêtre thrombectomie directe (≤ 6 h)", cls: "caution" };
  if (elapsed <= 24 * 60) return { label: "Imagerie de perfusion requise (DAWN / DEFUSE-3, 6-24 h)", cls: "caution" };
  return { label: "Hors fenêtres thérapeutiques (> 24 h)", cls: "stop" };
}

export default function StrokeCode() {
  const [patient, setPatient] = useState("");
  const [lkw, setLkw] = useState<string>("");
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  const elapsedMin = useMemo(() => {
    if (!lkw) return null;
    const d = new Date(lkw).getTime();
    if (Number.isNaN(d)) return null;
    return Math.round((now - d) / 60000);
  }, [lkw, now]);

  const band = bandOf(elapsedMin);

  // NIHSS : toutes les bornes à 0 par défaut
  const [nihssItems, setNihssItems] = useState<Record<string, number>>({});
  const nihssTotal = useMemo(
    () => Object.values(nihssItems).reduce((a, b) => a + b, 0),
    [nihssItems]
  );
  const [nihss, setNihss] = useState<NihssResult | null>(null);

  // ASPECTS : 10 régions saines par défaut (1)
  const [regions, setRegions] = useState<Record<string, number>>(() =>
    Object.fromEntries(ASPECTS_REGIONS.map((r) => [r.key, 1]))
  );
  const aspectsTotal = useMemo(
    () => Object.values(regions).reduce((a, b) => a + b, 0),
    [regions]
  );
  const [aspects, setAspects] = useState<AspectsResult | null>(null);

  const [contra, setContra] = useState<Record<string, boolean>>({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const nihssComplete = useMemo(
    () => NIHSS_ITEMS.every((i) => nihssItems[i.key] !== undefined),
    [nihssItems]
  );

  async function evaluate() {
    setBusy(true);
    setError("");
    try {
      const [n, a] = await Promise.all([
        postScore<{ resultat: NihssResult }>("neurology", "nihss", { items: nihssItems }),
        postScore<{ resultat: AspectsResult }>("neurology", "aspects", { scores_regions: regions }),
      ]);
      setNihss(n.resultat);
      setAspects(a.resultat);
    } catch (e) {
      setError(e instanceof Error ? e.message : "neurology-service injoignable");
    } finally {
      setBusy(false);
    }
  }

  /** Synthèse d'aide à la décision (front) à partir des résultats du moteur. */
  const decision: { verdict: string; cls: "go" | "caution" | "stop"; detail: string } | null =
    useMemo(() => {
      if (!nihss || !aspects || elapsedMin === null) return null;
      const contraCount = Object.values(contra).filter(Boolean).length;
      const inAlteplase = elapsedMin <= FENETRE_ALTEPLASE;
      const inThrombectomie = elapsedMin <= FENETRE_THROMBECTOMIE;
      if (elapsedMin > 24 * 60)
        return { verdict: "Hors fenêtres — traitement médical", cls: "stop",
                 detail: "Aucune revascularisation indiquée au-delà de 24 h après le LKW." };
      if (contraCount > 0 && inAlteplase)
        return { verdict: "Thrombolyse contre-indiquée — évaluer thrombectomie", cls: "caution",
                 detail: `${contraCount} contre-indication(s) cochée(s). La thrombectomie mécanique n'est pas soumise aux mêmes contre-indications : avis neuroradiologique immédiat.` };
      const thrombolyse = inAlteplase && nihss.thrombolyse_candidate && contraCount === 0;
      const thrombectomie = inThrombectomie && aspects.thrombectomie_candidate;
      if (thrombolyse && thrombectomie)
        return { verdict: "Candidat thrombolyse IV + thrombectomie", cls: "go",
                 detail: "NIHSS ≥ 4, ASPECTS ≥ 6, fenêtre ouverte, sans contre-indication : activer le plateau et prévenir le neuroradiologue." };
      if (thrombolyse)
        return { verdict: "Candidat thrombolyse IV (alteplase)", cls: "go",
                 detail: "Fenêtre ≤ 4,5 h et NIHSS ≥ 4 : porte-aiguille cible ≤ 60 min après l'arrivée." };
      if (thrombectomie)
        return { verdict: "Candidat thrombectomie mécanique", cls: "go",
                 detail: "ASPECTS ≥ 6 dans la fenêtre 0-6 h : transfert angiographie immédiat." };
      if (elapsedMin <= 24 * 60 && !inAlteplase)
        return { verdict: "Perfusion (CT/IRM) — discussion DAWN / DEFUSE-3", cls: "caution",
                 detail: "Au-delà de 6 h, la sélection repose sur l'imagerie de perfusion et l'appariement clinique." };
      return { verdict: "Non candidat à la revascularisation", cls: "stop",
               detail: !nihss.thrombolyse_candidate && nihss.score < 4
                 ? "NIHSS < 4 : thrombolyse non recommandée (déficit mineur non invalidant)."
                 : "Vérifier fenêtre, sévérité et contre-indications." };
    }, [nihss, aspects, contra, elapsedMin]);

  const markerPct = elapsedMin === null ? 0 : Math.min(100, (elapsedMin / 1440) * 100);

  return (
    <div>
      <h2>🧠 Code AVC — parcours stroke</h2>
      <p className="note">
        NIHSS (Lyden 2001) · ASPECTS (Barber, Lancet 2000) · fenêtres AHA/ASA — moteur{" "}
        <code>packages/clinical-rules</code> via neurology-service. Aide à la décision :
        ne remplace pas l'avis neurovasculaire.
      </p>
      {error && <p className="error">neurology-service : {error}</p>}

      {/* Bandeau horloge LKW */}
      <div className="card stroke-timer">
        <div className="stroke-timer-head">
          <div>
            <h3>Horloge code AVC</h3>
            <input
              type="text"
              placeholder="Patient (nom, salle…)"
              value={patient}
              onChange={(e) => setPatient(e.target.value)}
              style={{ marginTop: 6 }}
            />
          </div>
          <label className="stroke-lkw">
            Dernier vu normal (LKW)
            <input type="datetime-local" value={lkw} onChange={(e) => setLkw(e.target.value)} />
          </label>
          <div className="stroke-elapsed">
            <span className="kpi">
              {elapsedMin === null
                ? "—"
                : `${Math.floor(Math.max(0, elapsedMin) / 60)} h ${String(Math.max(0, elapsedMin) % 60).padStart(2, "0")}`}
            </span>
            <span className="sub">écoulées depuis le LKW</span>
          </div>
        </div>
        <div className="window-bar">
          <div className="window-seg alteplase" style={{ width: `${(270 / 1440) * 100}%` }} />
          <div className="window-seg thrombectomie" style={{ width: `${(90 / 1440) * 100}%` }} />
          <div className="window-seg perfusion" style={{ width: `${(1080 / 1440) * 100}%` }} />
          {elapsedMin !== null && elapsedMin >= 0 && (
            <div className="window-marker" style={{ left: `calc(${markerPct}% - 2px)` }} />
          )}
        </div>
        <div className="window-legend note">
          <span className="dot alteplase" /> alteplase ≤ 4,5 h
          <span className="dot thrombectomie" /> thrombectomie ≤ 6 h
          <span className="dot perfusion" /> perfusion 6-24 h
          <strong className={band.cls ? `decision-inline ${band.cls}` : ""}>{band.label}</strong>
        </div>
      </div>

      <div className="stroke-columns">
        {/* NIHSS */}
        <div className="card">
          <h3>NIHSS — 11 items (0-38)</h3>
          {!nihssComplete && <p className="note">Cotez les 13 champs pour activer le calcul.</p>}
          <div className="nihss-rows">
            {NIHSS_ITEMS.map((it) => (
              <label key={it.key} className="nihss-row">
                <span>{it.label}</span>
                <select
                  value={nihssItems[it.key] ?? ""}
                  onChange={(e) =>
                    setNihssItems((prev) => ({ ...prev, [it.key]: Number(e.target.value) }))
                  }
                >
                  <option value="" disabled>—</option>
                  {Array.from({ length: it.max + 1 }, (_, v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
              </label>
            ))}
          </div>
          <p style={{ margin: "10px 0 0" }}>
            Total cote : <strong>{nihssTotal}</strong> / 38{" "}
            {nihss && (
              <span className="badge ok">
                moteur : {nihss.score} — {nihss.gravite}
                {nihss.thrombolyse_candidate ? " · thrombolyse ≥ 4 ✓" : " · < 4"}
              </span>
            )}
          </p>
        </div>

        {/* ASPECTS + contre-indications */}
        <div>
          <div className="card">
            <h3>ASPECTS — 10 régions du territoire sylvien</h3>
            <div className="aspects-grid">
              {ASPECTS_REGIONS.map((r) => (
                <button
                  key={r.key}
                  type="button"
                  className={`aspects-chip ${regions[r.key] === 1 ? "saine" : "ischemie"}`}
                  onClick={() =>
                    setRegions((prev) => ({ ...prev, [r.key]: prev[r.key] === 1 ? 0 : 1 }))
                  }
                  title={`${r.label} — cliquer pour basculer saine / ischémie`}
                >
                  {r.label}
                  <em>{regions[r.key] === 1 ? "saine" : "ischémie"}</em>
                </button>
              ))}
            </div>
            <p style={{ margin: "10px 0 0" }}>
              ASPECTS : <strong>{aspectsTotal}</strong> / 10{" "}
              {aspectsTotal < 6 && <span className="badge critical">thrombectomie non candidate (&lt; 6)</span>}
              {aspectsTotal >= 6 && <span className="badge ok">≥ 6</span>}
              {aspects && <span className="note"> — moteur : {aspects.interpretation}</span>}
            </p>
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <h3>Contre-indications à la thrombolyse</h3>
            <div className="check-grid">
              {CONTRAINDICATIONS.map((c, i) => (
                <label key={c} className="chk">
                  <input
                    type="checkbox"
                    checked={contra[String(i)] ?? false}
                    onChange={(e) => setContra((prev) => ({ ...prev, [String(i)]: e.target.checked }))}
                  />
                  {c}
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Synthèse */}
      <div className={`decision-banner ${decision?.cls ?? ""}`}>
        {decision ? (
          <>
            <div className="decision-verdict">{decision.verdict}</div>
            <div className="decision-detail">{decision.detail}</div>
            <div className="note" style={{ marginTop: 6 }}>
              {patient ? `Patient : ${patient} — ` : ""}
              LKW {elapsedMin} min · NIHSS {nihss?.score} · ASPECTS {aspects?.score} —
              décision finale : neurologue + neuroradiologue (double validation).
            </div>
          </>
        ) : (
          <div className="decision-detail">
            Renseignez l'horloge LKW, le NIHSS complet et l'ASPECTS, puis lancez
            l'évaluation moteur pour obtenir la synthèse d'orientation.
          </div>
        )}
      </div>

      <button onClick={evaluate} disabled={busy || !nihssComplete} style={{ marginTop: 14 }}>
        {busy ? "Évaluation…" : "Évaluer NIHSS + ASPECTS (moteur clinique)"}
      </button>
      {!nihssComplete && (
        <span className="note" style={{ marginLeft: 10 }}>
          NIHSS incomplet ({Object.keys(nihssItems).length}/13 cotes)
        </span>
      )}
    </div>
  );
}
