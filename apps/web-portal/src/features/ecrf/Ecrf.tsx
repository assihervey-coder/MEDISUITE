/**
 * Écran eCRF — investigation MEDISUITE-CI-01 (R5/R6, v0.7).
 *
 * Saisie offline-first des formulaires F01-F06 (protocole TD-10, annexe A1) :
 * hors connexion, les soumissions partent dans la file IndexedDB et sont
 * rejouées automatiquement avec idempotence (aucun doublon possible côté
 * serveur). Signature investigateur (verrou) depuis la liste des sujets.
 */
import { useCallback, useEffect, useMemo, useState, type CSSProperties } from "react";
import { api, isQueuedReceipt, submitWithQueue } from "../../services/api";
import { useOfflineStore } from "../../offline/offlineStore";

const BASE = "/api/ecrf/api/v1/ecrf";

interface FieldDef {
  id: string;
  type: "str" | "text" | "enum" | "int" | "float" | "bool" | "date" | "datetime";
  required?: boolean;
  choices?: string[];
  min?: number;
  max?: number;
  libelle?: string;
}

interface FormDef {
  id: string;
  titre: string;
  role: string;
  fields: FieldDef[];
}

interface Catalogue {
  study: string;
  version: string;
  sites: Record<string, string>;
  scenarios: Record<string, string>;
  forms: FormDef[];
}

interface Subject {
  code: string;
  site: string;
  scenario: string;
  statut: string;
  motif: string;
}

interface EntryRef {
  id: string;
  form_id: string;
  version: number;
  statut: string;
  signed_by?: string | null;
  parent_id?: string | null;
}

const inputStyle: CSSProperties = {
  width: "100%", padding: "6px 8px", borderRadius: 4,
  border: "1px solid #b8c7d6", fontSize: 13, boxSizing: "border-box",
};

export default function Ecrf() {
  const { online, pending } = useOfflineStore();
  const [cat, setCat] = useState<Catalogue | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selected, setSelected] = useState<Subject | null>(null);
  const [entries, setEntries] = useState<EntryRef[]>([]);
  const [formId, setFormId] = useState<string>("F03-DECISION");
  const [payload, setPayload] = useState<Record<string, unknown>>({});
  const [message, setMessage] = useState<string>("");
  const [busy, setBusy] = useState(false);

  const [newSubject, setNewSubject] = useState({
    site: "COC", scenario: "S1", consentement: "ecrit",
    age: 45, perte_modalites: 0,
  });
  const [showNew, setShowNew] = useState(false);

  const reloadSubjects = useCallback(async () => {
    try {
      const r = await api.get<{ subjects: Subject[] }>(`${BASE}/subjects`);
      setSubjects(r.subjects);
    } catch {
      setMessage("Liste des sujets indisponible hors-ligne (non mise en cache).");
    }
  }, []);

  useEffect(() => {
    void (async () => {
      try {
        setCat(await api.get<Catalogue>(`${BASE}/forms`));
        await reloadSubjects();
      } catch {
        setMessage("eCRF inaccessible — vérifiez la connexion (saisie possible via file offline).");
      }
    })();
  }, [reloadSubjects]);

  const openSubject = useCallback(async (code: string) => {
    setMessage("");
    try {
      const r = await api.get<Subject & { entries: EntryRef[] }>(`${BASE}/subjects/${code}`);
      const { entries: e, ...s } = r;
      setSelected(s);
      setEntries(e);
    } catch {
      setMessage("Détail sujet indisponible (hors-ligne).");
    }
  }, []);

  const form = useMemo(
    () => cat?.forms.find((f) => f.id === formId) ?? null,
    [cat, formId],
  );

  const setField = (id: string, value: unknown) =>
    setPayload((p) => ({ ...p, [id]: value }));

  const submit = async () => {
    if (!selected || !form) return;
    setBusy(true);
    setMessage("");
    try {
      const out = await submitWithQueue(
        `${BASE}/subjects/${selected.code}/forms/${form.id}`,
        payload,
      );
      if (isQueuedReceipt(out)) {
        setMessage(`Saisie ${form.id} empilée hors-ligne (clé ${out.clientKey.slice(0, 8)}…) — rejeu automatique au retour du réseau.`);
      } else {
        setMessage(out && typeof out === "object" && "duplicate" in out && out.duplicate
          ? "Saisie déjà enregistrée (idempotence) — rien créé."
          : `Saisie ${form.id} enregistrée côté serveur.`);
        await openSubject(selected.code);
      }
      setPayload({});
    } catch (err) {
      setMessage(`Erreur : ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setBusy(false);
    }
  };

  const sign = async (entryId: string) => {
    setBusy(true);
    try {
      await api.post(`${BASE}/entries/${entryId}/sign`);
      setMessage("Entrée signée et verrouillée (ISO 14155 §4.8).");
      if (selected) await openSubject(selected.code);
    } catch (err) {
      setMessage(`Erreur de signature : ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setBusy(false);
    }
  };

  const createSubject = async () => {
    setBusy(true);
    setMessage("");
    try {
      const out = await submitWithQueue(`${BASE}/subjects`, { ...newSubject, date_passage: new Date().toISOString().slice(0, 10) });
      if (isQueuedReceipt(out)) {
        setMessage("Inclusion empilée hors-ligne — elle sera rejouée au retour du réseau.");
      } else {
        const r = out as unknown as Subject;
        setMessage(`Sujet ${r.code} inclus (${r.statut}).`);
        await reloadSubjects();
        await openSubject(r.code);
      }
      setShowNew(false);
    } catch (err) {
      setMessage(`Erreur d'inclusion : ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h1>📋 eCRF — Investigation {cat?.study ?? "MEDISUITE-CI-01"}</h1>
      <p style={{ color: "#5b7186", fontSize: 13 }}>
        Protocole R5 (ISO 14155) · saisie offline-first · idempotence serveur ·{" "}
        {online
          ? `en ligne${pending > 0 ? ` · ${pending} saisie(s) en attente de sync` : ""}`
          : "HORS CONNEXION — les saisies sont mises en file locale"}
      </p>
      {message && (
        <p style={{ background: "#eaf2fb", border: "1px solid #b8cfe8",
                    padding: "8px 12px", borderRadius: 6, fontSize: 13 }}>
          {message}
        </p>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 16 }}>
        {/* Colonne sujets */}
        <section style={{ background: "#fff", borderRadius: 8, padding: 12,
                          border: "1px solid #dbe4ec" }}>
          <h3 style={{ marginTop: 0 }}>Sujets ({subjects.length})</h3>
          <button onClick={() => setShowNew(!showNew)}
                  style={{ marginBottom: 8, width: "100%" }}>
            {showNew ? "Annuler" : "+ Inclure un sujet"}
          </button>
          {showNew && (
            <div style={{ display: "grid", gap: 6, marginBottom: 10,
                          fontSize: 13 }}>
              <select style={inputStyle} value={newSubject.site}
                      onChange={(e) => setNewSubject({ ...newSubject, site: e.target.value })}>
                {Object.entries(cat?.sites ?? {}).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
              <select style={inputStyle} value={newSubject.scenario}
                      onChange={(e) => setNewSubject({ ...newSubject, scenario: e.target.value })}>
                {Object.entries(cat?.scenarios ?? {}).map(([k, v]) => (
                  <option key={k} value={k}>{k} — {v}</option>
                ))}
              </select>
              <input style={inputStyle} type="number" min={18} max={120}
                     value={newSubject.age} placeholder="âge"
                     onChange={(e) => setNewSubject({ ...newSubject, age: Number(e.target.value) })} />
              <select style={inputStyle} value={newSubject.consentement}
                      onChange={(e) => setNewSubject({ ...newSubject, consentement: e.target.value })}>
                <option value="ecrit">Consentement écrit</option>
                <option value="differe_urgence">Différé urgence (ISO 14155 §6.7)</option>
              </select>
              <button disabled={busy} onClick={() => void createSubject()}>
                Créer l'inclusion
              </button>
            </div>
          )}
          <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: 13 }}>
            {subjects.map((s) => (
              <li key={s.code}>
                <button
                  onClick={() => void openSubject(s.code)}
                  style={{
                    width: "100%", textAlign: "left", background: "none",
                    border: "none", padding: "6px 4px", cursor: "pointer",
                    fontWeight: selected?.code === s.code ? 700 : 400,
                    borderBottom: "1px solid #eef2f6",
                  }}
                >
                  {s.code} · {s.scenario}{" "}
                  <span style={{ color: s.statut === "inclus" ? "#15803d" : "#b45309" }}>
                    ({s.statut})
                  </span>
                </button>
              </li>
            ))}
            {subjects.length === 0 && <li style={{ color: "#5b7186" }}>Aucun sujet (ou hors-ligne).</li>}
          </ul>
        </section>

        {/* Colonne saisie */}
        <section style={{ display: "grid", gap: 16 }}>
          {selected && (
            <div style={{ background: "#fff", borderRadius: 8, padding: 12,
                          border: "1px solid #dbe4ec" }}>
              <h3 style={{ marginTop: 0 }}>
                {selected.code} — {cat?.scenarios[selected.scenario] ?? selected.scenario}
              </h3>
              <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
                <thead>
                  <tr><th align="left">Formulaire</th><th>v</th><th>Statut</th><th>Signé par</th><th></th></tr>
                </thead>
                <tbody>
                  {entries.map((e) => (
                    <tr key={e.id}>
                      <td>{e.form_id}{e.parent_id ? " (amendement)" : ""}</td>
                      <td align="center">{e.version}</td>
                      <td align="center">{e.statut}</td>
                      <td align="center">{e.signed_by ?? "—"}</td>
                      <td align="right">
                        {e.statut === "brouillon" && (
                          <button disabled={busy} onClick={() => void sign(e.id)}>
                            ✍️ Signer
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {entries.length === 0 && (
                    <tr><td colSpan={5}>Aucune entrée (F01 à la création).</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {selected && form && (
            <div style={{ background: "#fff", borderRadius: 8, padding: 12,
                          border: "1px solid #dbe4ec" }}>
              <h3 style={{ marginTop: 0 }}>
                Saisie — {form.id}
              </h3>
              <p style={{ fontSize: 13, color: "#5b7186", marginTop: 0 }}>
                {form.titre} · rôle requis : {form.role}
              </p>
              <select style={{ ...inputStyle, marginBottom: 10 }}
                      value={formId}
                      onChange={(e) => { setFormId(e.target.value); setPayload({}); }}>
                {(cat?.forms ?? []).map((f) => (
                  <option key={f.id} value={f.id}>{f.id}</option>
                ))}
              </select>
              <div style={{ display: "grid", gap: 8 }}>
                {form.fields.map((f) => (
                  <label key={f.id} style={{ fontSize: 13 }}>
                    <strong>{f.id}</strong>
                    {f.libelle ? ` — ${f.libelle}` : ""}
                    {f.required ? " *" : ""}
                    <div style={{ marginTop: 3 }}>
                      {f.type === "enum" ? (
                        <select style={inputStyle}
                                value={String(payload[f.id] ?? "")}
                                onChange={(e) => setField(f.id, e.target.value)}>
                          <option value="">— choisir —</option>
                          {(f.choices ?? []).map((c) => <option key={c} value={c}>{c}</option>)}
                        </select>
                      ) : f.type === "bool" ? (
                        <input type="checkbox" checked={payload[f.id] === true}
                               onChange={(e) => setField(f.id, e.target.checked)} />
                      ) : f.type === "int" || f.type === "float" ? (
                        <input style={inputStyle} type="number" step={f.type === "float" ? 0.1 : 1}
                               value={payload[f.id] === undefined ? "" : String(payload[f.id])}
                               onChange={(e) => setField(f.id, f.type === "int" ? parseInt(e.target.value, 10) : parseFloat(e.target.value))} />
                      ) : f.type === "date" ? (
                        <input style={inputStyle} type="date" value={String(payload[f.id] ?? "")}
                               onChange={(e) => setField(f.id, e.target.value)} />
                      ) : f.type === "datetime" ? (
                        <input style={inputStyle} type="datetime-local"
                               value={String(payload[f.id] ?? "").slice(0, 16)}
                               onChange={(e) => setField(f.id, e.target.value)} />
                      ) : f.type === "text" ? (
                        <textarea style={inputStyle} rows={2} value={String(payload[f.id] ?? "")}
                                  onChange={(e) => setField(f.id, e.target.value)} />
                      ) : (
                        <input style={inputStyle} value={String(payload[f.id] ?? "")}
                               onChange={(e) => setField(f.id, e.target.value)} />
                      )}
                    </div>
                  </label>
                ))}
              </div>
              <button disabled={busy} onClick={() => void submit()}
                      style={{ marginTop: 12 }}>
                {online ? "Enregistrer" : "Enregistrer hors-ligne (file)"}
              </button>
            </div>
          )}

          {!selected && (
            <div style={{ background: "#fff", borderRadius: 8, padding: 16,
                          border: "1px dashed #b8c7d6", fontSize: 13,
                          color: "#5b7186" }}>
              Sélectionnez un sujet (ou incluez-en un) pour saisir les
              formulaires F01-F06 du protocole {cat?.study}. La saisie
              fonctionne hors connexion : les formulaires partent en file
              locale et sont rejoués automatiquement — le serveur dédoublonne
              par clé calculée, donc aucun risque de doublon.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
