/** Gabarit « liste des cas » des écrans fins (v0.14) — recherche + filtres
 *  statut/sévérité (logique pure testée), création de cas (RBAC serveur),
 *  navigation vers la fiche détail. */
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../services/api";
import { distinct, filterCases, siblingRoute } from "../logic";
import type { CaseRow, ScreenDef } from "../types";
import { useI18n } from "../../i18n/i18n";
import type { MsgKey } from "../../i18n/resolve";

export default function CaseListScreen({ screen }: { screen: ScreenDef }) {
  const { t } = useI18n();
  const [cases, setCases] = useState<CaseRow[] | null>(null);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [statut, setStatut] = useState("");
  const [severite, setSeverite] = useState("");
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ patient_id: "pat0001", patient_nom: "", titre: "", date: "" });

  const reload = () =>
    api
      .get<CaseRow[]>(`/api/specialty/${screen.urlSlug}/api/v1/cases`)
      .then(setCases)
      .catch((e) => {
        setCases([]);
        setError(e.message);
      });

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen.urlSlug]);

  const shown = useMemo(
    () => filterCases(cases ?? [], q, statut, severite),
    [cases, q, statut, severite],
  );

  const createCase = async () => {
    if (form.titre.trim() === "") return;
    try {
      await api.post<CaseRow>(`/api/specialty/${screen.urlSlug}/api/v1/cases`, {
        ...form,
        date: form.date || new Date().toISOString().slice(0, 10),
        payload: {},
      });
      setForm({ patient_id: "pat0001", patient_nom: "", titre: "", date: "" });
      setCreating(false);
      setError("");
      reload();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div>
      <nav aria-label="breadcrumb" className="note">
        <Link to={siblingRoute(screen, "overview")}>
          {screen.icon} {t(`mod.${screen.slug}` as MsgKey)}
        </Link>
        {" · "}
        {t("scr.cas")}
      </nav>
      <h2>
        {screen.icon} {t(`mod.${screen.slug}` as MsgKey)} — {t("scr.cas")}
      </h2>
      {error && (
        <p className="error">
          {t("scr.unreachable")} ({error})
        </p>
      )}

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", margin: "8px 0 16px" }}>
        <input
          placeholder={t("scr.search")}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ flex: "1 1 180px" }}
        />
        <select value={statut} onChange={(e) => setStatut(e.target.value)} aria-label={t("scr.filter_status")}>
          <option value="">{t("scr.filter_status")} — {t("scr.all")}</option>
          {distinct(cases ?? [], "statut").map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select value={severite} onChange={(e) => setSeverite(e.target.value)} aria-label={t("scr.filter_severity")}>
          <option value="">{t("scr.filter_severity")} — {t("scr.all")}</option>
          {distinct(cases ?? [], "severite").map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button onClick={() => setCreating((v) => !v)}>＋ {t("scr.new_case")}</button>
      </div>

      {creating && (
        <div style={{ border: "1px dashed rgba(255,255,255,.3)", padding: 12, marginBottom: 12 }}>
          <input placeholder={t("scr.patient_id")} value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <input placeholder={t("scr.patient_name")} value={form.patient_nom} onChange={(e) => setForm({ ...form, patient_nom: e.target.value })} />
          <input placeholder={t("scr.case_title")} value={form.titre} onChange={(e) => setForm({ ...form, titre: e.target.value })} />
          <input type="date" aria-label={t("scr.date")} value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
          <div style={{ marginTop: 8 }}>
            <button onClick={createCase}>{t("scr.create")}</button>
          </div>
        </div>
      )}

      <table>
        <thead>
          <tr>
            <th>{t("scr.patient_name")}</th>
            <th>{t("scr.case_title")}</th>
            <th>{t("scr.filter_severity")}</th>
            <th>{t("scr.filter_status")}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {shown.map((c) => (
            <tr key={c.id}>
              <td>{c.patient_nom || c.patient_id || "—"}</td>
              <td>{c.titre}</td>
              <td>
                <span className="badge warn">{c.severite || "—"}</span>
              </td>
              <td>{c.statut ?? "actif"}</td>
              <td>
                <Link to={`${siblingRoute(screen, "cas")}/${c.id}`}>{t("scr.open_detail")}</Link>
              </td>
            </tr>
          ))}
          {cases !== null && shown.length === 0 && !error && (
            <tr>
              <td colSpan={5} className="note">
                {t("scr.empty")}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
