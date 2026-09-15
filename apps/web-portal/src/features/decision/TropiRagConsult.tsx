/** Aide à la décision clinique — TropiRAG intégré (fièvre + voyage, Afrique de l'Ouest).
 *
 *  Analyse un cas via le moteur déterministe TropiRAG (170 règles cliniques,
 *  safety gate, RAG sur 47 unités de preuve OMS/CDC/MSF citées) et affiche :
 *  urgence, gravité, red flags, différentiels pondérés, tests requis,
 *  contraintes médicamenteuses, narrative et citations sourcées.
 *
 *  Principe affiché : IA ≠ autorité clinique — la décision reste médicale. */
import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { toast } from "../../store/toastStore";
import {
  buildCasePayload, dedupeTests, meshBadgeLabel, meshFromNodesReport, pickLabel,
  SEVERITY_LABEL, SYMPTOM_FALLBACK, TR_COUNTRIES, TR_FORM_DEFAULT, urgencyClass,
  URGENCY_LABEL, type TrCaseResult, type TrForm, type TrMesh, type TrSymptom,
} from "./tropirag";

export default function TropiRagConsult() {
  const [form, setForm] = useState<TrForm>(TR_FORM_DEFAULT);
  const [symptoms, setSymptoms] = useState<TrSymptom[]>(SYMPTOM_FALLBACK);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<TrCaseResult | null>(null);
  const [error, setError] = useState("");
  const [mesh, setMesh] = useState<TrMesh | null>(null);
  const [useAi, setUseAi] = useState(false);

  // Taxonomie des symptômes fournie par le backend TropiRAG (repli local sinon).
  useEffect(() => {
    api.get<{ symptoms: TrSymptom[] }>("/api/tropirag/api/v1/symptoms/taxonomy")
      .then((t) => { if (t.symptoms?.length) setSymptoms(t.symptoms); })
      .catch(() => { /* repli SYMPTOM_FALLBACK déjà en place */ });
    // Mesh LLM local : état des nœuds Ollama (TROPIRAG_OLLAMA_URL / _NODES).
    api.get<Parameters<typeof meshFromNodesReport>[0]>(
      "/api/tropirag/api/v1/inference/nodes",
    ).then((r) => setMesh(meshFromNodesReport(r)))
      .catch(() => setMesh({ mode: "deterministic", nodeUp: false, nodeCount: 0 }));
  }, []);

  const toggleSymptom = (code: string): void =>
    setForm((f) => ({
      ...f,
      symptoms: f.symptoms.includes(code) ? f.symptoms.filter((c) => c !== code) : [...f.symptoms, code],
    }));

  async function analyze(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formEl = e.currentTarget; // capturé AVANT le await
    setBusy(true);
    setError("");
    try {
      const r = await api.post<TrCaseResult>(
        "/api/tropirag/api/v1/cases", buildCasePayload(form, useAi));
      setResult(r);
      formEl.reset();
      const n = dedupeTests(r.required_tests).length;
      toast.ok(
        `Analyse TropiRAG : ${URGENCY_LABEL[r.urgency] ?? r.urgency}` +
        (r.differentials?.length ? ` — ${r.differentials.length} hypothèse(s), ${n} examen(s)` : ""),
      );
    } catch (err) {
      setError((err as Error).message);
      toast.error(`TropiRAG : ${(err as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  function reset() { setForm(TR_FORM_DEFAULT); setResult(null); setError(""); }

  return (
    <div>
      <h2>🧭 Aide à la décision — TropiRAG{" "}
        <span
          className={`badge ${mesh && mesh.mode !== "deterministic" && mesh.nodeUp ? "ok" : "warn"}`}
          data-testid="tr-mesh"
          title="État du mesh LLM local (nœuds Ollama) — la synthèse IA reste sous Safety Gate"
        >
          {meshBadgeLabel(mesh)}
        </span>
      </h2>
      <p className="banner warn" style={{ marginTop: 8 }}>
        <strong>IA ≠ autorité clinique.</strong> Le moteur applique 170 règles OMS déterministes et
        cite ses sources (OMS · CDC · MSF) — la décision reste médicale. Usage : fièvre + voyage,
        Afrique de l'Ouest.
      </p>

      <form onSubmit={analyze} style={{ marginTop: 12 }}>
        <div className="detail-grid">
          <div className="card">
            <h3>Patient &amp; constantes</h3>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <label style={{ flex: 1, minWidth: 90 }}>
                Âge
                <input type="number" min={0} max={120} required value={form.age}
                  onChange={(e) => setForm({ ...form, age: Number(e.target.value) })} style={{ width: "100%" }} />
              </label>
              <label style={{ flex: 1, minWidth: 130 }}>
                Sexe
                <select value={form.sex} onChange={(e) => setForm({ ...form, sex: e.target.value as TrForm["sex"] })} style={{ width: "100%" }}>
                  <option value="female">Féminin</option>
                  <option value="male">Masculin</option>
                  <option value="unknown">Non précisé</option>
                </select>
              </label>
              <label style={{ flex: 1, minWidth: 150 }}>
                Grossesse
                <select value={form.pregnant} onChange={(e) => setForm({ ...form, pregnant: e.target.value as TrForm["pregnant"] })} style={{ width: "100%" }}>
                  <option value="not_applicable">Non applicable</option>
                  <option value="pregnant">Enceinte</option>
                  <option value="possibly_pregnant">Peut-être enceinte</option>
                  <option value="not_pregnant">Non enceinte</option>
                </select>
              </label>
              <label style={{ flex: 1, minWidth: 110 }}>
                Température (°C)
                <input type="number" step="0.1" min={34} max={44} value={form.temperatureC ?? ""}
                  onChange={(e) => setForm({ ...form, temperatureC: e.target.value === "" ? null : Number(e.target.value) })} style={{ width: "100%" }} />
              </label>
            </div>

            <h3 style={{ marginTop: 14 }}>Voyage / exposition</h3>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
              <label style={{ flex: 1, minWidth: 160 }}>
                Pays visité
                <select value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} style={{ width: "100%" }}>
                  {TR_COUNTRIES.map((c) => <option key={c.code} value={c.code}>{c.label}</option>)}
                </select>
              </label>
              <label style={{ flex: 1, minWidth: 120 }}>
                Retour depuis (j)
                <input type="number" min={0} max={365} value={form.daysBack ?? ""}
                  onChange={(e) => setForm({ ...form, daysBack: e.target.value === "" ? null : Number(e.target.value) })} style={{ width: "100%" }} />
              </label>
            </div>
            <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginTop: 8 }}>
              <label><input type="checkbox" checked={form.rural} onChange={(e) => setForm({ ...form, rural: e.target.checked })} /> séjour rural</label>
              <label><input type="checkbox" checked={form.forest} onChange={(e) => setForm({ ...form, forest: e.target.checked })} /> zone forestière</label>
              <label><input type="checkbox" checked={form.stagnantWater} onChange={(e) => setForm({ ...form, stagnantWater: e.target.checked })} /> eaux stagnantes</label>
            </div>

            <h3 style={{ marginTop: 14 }}>Laboratoire</h3>
            <label style={{ display: "block", maxWidth: 240 }}>
              TDR paludisme
              <select value={form.rdtMalaria} onChange={(e) => setForm({ ...form, rdtMalaria: e.target.value as TrForm["rdtMalaria"] })} style={{ width: "100%" }}>
                <option value="">— non réalisé —</option>
                <option value="positif">Positif</option>
                <option value="negatif">Négatif</option>
              </select>
            </label>
          </div>

          <div className="card">
            <h3>Symptômes ({form.symptoms.length} sélectionné(s))</h3>
            <div className="modality-picker" data-testid="tr-symptoms">
              {symptoms.map((s) => (
                <button
                  key={s.code} type="button"
                  className={`modality-chip ${form.symptoms.includes(s.code) ? "on" : ""}`}
                  onClick={() => toggleSymptom(s.code)}
                  title={s.code}
                >
                  {s.fr || s.code}
                </button>
              ))}
            </div>
            <h3 style={{ marginTop: 14 }}>Contexte libre</h3>
            <textarea
              rows={3} placeholder="Anamnèse complémentaire (optionnel)…"
              value={form.freeText}
              onChange={(e) => setForm({ ...form, freeText: e.target.value })}
              style={{ width: "100%" }}
            />
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center", flexWrap: "wrap" }}>
          <button type="submit" disabled={busy} data-testid="tr-analyze" className="primary">
            {busy ? "Analyse…" : "▶ Analyser le cas (règles + RAG)"}
          </button>
          <button type="button" onClick={reset} disabled={busy}>Réinitialiser</button>
          {mesh && mesh.mode !== "deterministic" && mesh.nodeUp && (
            <label
              style={{ marginLeft: "auto" }}
              title="Ajoute une synthèse rédigée par le LLM local du mesh (Med42). Le Safety Gate l'audite : couverture des preuves, aucune invention — refus possible."
            >
              <input
                type="checkbox"
                checked={useAi}
                onChange={(e) => setUseAi(e.target.checked)}
                data-testid="tr-use-ai"
              />{" Synthèse IA du mesh (auditée)"}
            </label>
          )}
        </div>
      </form>

      {error && <p className="error" style={{ marginTop: 12 }}>Erreur TropiRAG : {error}</p>}

      {result && (
        <div style={{ marginTop: 20 }} data-testid="tr-result">
          <h3>Résultat de l'analyse {result.case_id ? <code style={{ fontSize: 12 }}>{result.case_id}</code> : ""}</h3>

          <p>
            Urgence : <span className={`badge ${urgencyClass(result.urgency)}`}>
              {URGENCY_LABEL[result.urgency] ?? result.urgency}
            </span>{" "}
            Gravité : <span className={`badge ${result.severity === "severe" ? "critical" : result.severity === "moderate" ? "warn" : "ok"}`}>
              {SEVERITY_LABEL[result.severity] ?? result.severity}
            </span>
          </p>

          {(result.red_flags?.length ?? 0) > 0 && (
            <div className="banner warn" role="alert" data-testid="tr-redflags">
              <strong>🚩 Signes d'alerte :</strong>
              <ul style={{ margin: "6px 0 0 18px" }}>
                {result.red_flags!.map((rf, i) => <li key={i}>{pickLabel(rf, ["code", "flag", "rule_id"])}</li>)}
              </ul>
            </div>
          )}

          {(result.escalations?.length ?? 0) > 0 && (
            <div className="banner warn" style={{ marginTop: 8 }}>
              <strong>⬆ Escalade :</strong>
              <ul style={{ margin: "6px 0 0 18px" }}>
                {result.escalations!.map((esc, i) => <li key={i}>{pickLabel(esc, ["level", "target"])}</li>)}
              </ul>
            </div>
          )}

          {(result.differentials?.length ?? 0) > 0 && (
            <>
              <h4 style={{ marginTop: 16 }}>Hypothèses diagnostiques pondérées</h4>
              {result.differentials!.map((d, i) => {
                const pct = Math.round((d.probability ?? 0) * 100);
                return (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, margin: "6px 0" }}>
                    <strong style={{ minWidth: 140 }}>{d.disease ?? "?"}</strong>
                    <div style={{ flex: 1, background: "var(--muted)", opacity: 0.25, borderRadius: 4, height: 12, overflow: "hidden" }}>
                      <div style={{ width: `${pct}%`, height: "100%", background: "var(--accent, #2b7a9e)" }} />
                    </div>
                    <span style={{ minWidth: 44, textAlign: "right" }}>{pct} %</span>
                  </div>
                );
              })}
            </>
          )}

          {dedupeTests(result.required_tests).length > 0 && (
            <>
              <h4 style={{ marginTop: 16 }}>Examens requis (test-first)</h4>
              <div className="modality-picker">
                {dedupeTests(result.required_tests).map((t) => (
                  <span key={t} className="modality-chip on" style={{ cursor: "default" }}>{t}</span>
                ))}
              </div>
            </>
          )}

          {(result.drug_constraints?.length ?? 0) > 0 && (
            <>
              <h4 style={{ marginTop: 16 }}>Contraintes médicamenteuses</h4>
              <ul>
                {result.drug_constraints!.map((dc, i) => (
                  <li key={i}>{pickLabel(dc, ["name", "constraint_type", "note"])}{dc.rationale ? ` — ${String(dc.rationale)}` : ""}</li>
                ))}
              </ul>
            </>
          )}

          {result.ai_synthesis && (
            <>
              <h4 style={{ marginTop: 16 }}>Synthèse IA du mesh local — auditée par le Safety Gate</h4>
              <p
                style={{ whiteSpace: "pre-wrap", background: "rgba(106,154,122,.10)", padding: 12, borderRadius: 8, border: "1px solid rgba(106,154,122,.35)" }}
                data-testid="tr-ai-synthesis"
              >
                {result.ai_synthesis}
              </p>
              <p className="note">Couche finale : {result.ai_layer === "ai-validated"
                ? "IA validée (couverture de preuves vérifiée)"
                : "déterministe"} — la décision reste médicale.</p>
            </>
          )}

          {result.narrative && (
            <>
              <h4 style={{ marginTop: 16 }}>Synthèse clinique déterministe</h4>
              <p style={{ whiteSpace: "pre-wrap", background: "rgba(127,127,127,.08)", padding: 12, borderRadius: 8 }}>
                {result.narrative}
              </p>
            </>
          )}

          {result.refusal && (
            <div className="banner warn" style={{ marginTop: 10 }}>
              <strong>Refus moteur :</strong> {result.refusal}
            </div>
          )}

          {(result.citations?.length ?? 0) > 0 && (
            <>
              <h4 style={{ marginTop: 16 }}>Sources citées (RAG)</h4>
              <ol style={{ fontSize: 13 }}>
                {result.citations!.map((c, i) => (
                  <li key={c.unit_id ?? i} style={{ margin: "4px 0" }}>
                    {c.full ?? c.unit_id}
                    {c.quote ? <em style={{ display: "block", color: "var(--muted)" }}>« {c.quote} »</em> : ""}
                  </li>
                ))}
              </ol>
            </>
          )}

          {result.disclaimer && <p className="note">{result.disclaimer}</p>}
        </div>
      )}
    </div>
  );
}
