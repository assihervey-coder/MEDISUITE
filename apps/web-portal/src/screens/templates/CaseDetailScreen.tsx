/** Gabarit « fiche cas » des écrans fins (v0.14) — détail du cas + calculateurs
 *  de scores réels : un bloc par endpoint de score, paramètres générés depuis
 *  les signatures de packages/clinical-rules (source unique), résultat brut
 *  affiché tel que renvoyé par le service (aucune réinterprétation UI). */
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, postScore } from "../../services/api";
import { buildScoreBody, paramInputKind, siblingRoute } from "../logic";
import type { CaseRow, ScreenDef } from "../types";
import { useI18n } from "../../i18n/i18n";
import type { MsgKey } from "../../i18n/resolve";

type Values = Record<string, string | boolean>;
type Outcome = { ok: boolean; text: string };

export default function CaseDetailScreen({ screen }: { screen: ScreenDef }) {
  const { t } = useI18n();
  const { caseId } = useParams<{ caseId: string }>();
  const [cases, setCases] = useState<CaseRow[] | null>(null);
  const [error, setError] = useState("");
  const [values, setValues] = useState<Record<string, Values>>({});
  const [outcomes, setOutcomes] = useState<Record<string, Outcome>>({});

  useEffect(() => {
    api
      .get<CaseRow[]>(`/api/specialty/${screen.urlSlug}/api/v1/cases`)
      .then(setCases)
      .catch((e) => {
        setCases([]);
        setError(e.message);
      });
  }, [screen.urlSlug]);

  const found = useMemo(
    () => (cases ?? []).find((c) => c.id === caseId) ?? null,
    [cases, caseId],
  );

  const evaluate = async (endpoint: string, fn: string) => {
    const sig = screen.sigs.find((s) => s.endpoint === endpoint);
    if (!sig) return;
    try {
      const res = await postScore<{ resultat: unknown }>(
        screen.urlSlug,
        endpoint,
        buildScoreBody(sig.params, values[endpoint] ?? {}),
      );
      setOutcomes((o) => ({
        ...o,
        [endpoint]: { ok: true, text: JSON.stringify(res.resultat, null, 2) },
      }));
    } catch (e) {
      setOutcomes((o) => ({
        ...o,
        [endpoint]: { ok: false, text: `${t("scr.calc_error")} : ${(e as Error).message} (${fn})` },
      }));
    }
  };

  return (
    <div>
      <nav aria-label="breadcrumb" className="note">
        <Link to={siblingRoute(screen, "overview")}>
          {screen.icon} {t(`mod.${screen.slug}` as MsgKey)}
        </Link>
        {" · "}
        <Link to={siblingRoute(screen, "cas")}>{t("scr.cas")}</Link>
        {" · "}
        {t("scr.detail")}
      </nav>
      <h2>
        {screen.icon} {t(`mod.${screen.slug}` as MsgKey)} — {t("scr.detail")}
      </h2>
      {error && (
        <p className="error">
          {t("scr.unreachable")} ({error})
        </p>
      )}
      {cases !== null && !found && !error && <p className="note">{t("scr.case_not_found")}</p>}

      {found && (
        <>
          <table>
            <tbody>
              <tr><th>{t("scr.patient_name")}</th><td>{found.patient_nom || found.patient_id || "—"}</td></tr>
              <tr><th>{t("scr.case_title")}</th><td>{found.titre}</td></tr>
              <tr><th>{t("scr.date")}</th><td>{found.date || "—"}</td></tr>
              <tr><th>{t("scr.filter_severity")}</th><td>{found.severite || "—"}</td></tr>
              <tr><th>{t("scr.filter_status")}</th><td>{found.statut ?? "actif"}</td></tr>
              <tr>
                <th>{t("scr.payload")}</th>
                <td>
                  <pre style={{ whiteSpace: "pre-wrap" }}>
                    {JSON.stringify(found.payload ?? {}, null, 2)}
                  </pre>
                </td>
              </tr>
            </tbody>
          </table>

          <h3>{t("scr.calc_title")}</h3>
          {screen.sigs.length === 0 && <p className="note">{t("scr.no_scores")}</p>}
          {screen.sigs.map((sig) => (
            <fieldset key={sig.endpoint} style={{ marginBottom: 12 }}>
              <legend>
                <code>{sig.endpoint}</code> · {sig.fn} ()
              </legend>
              {sig.params.length === 0 && <p className="note">{t("scr.calc_no_params")}</p>}
              {sig.params.map((p) => (
                <label key={p.name} style={{ display: "inline-flex", alignItems: "center", gap: 6, marginRight: 14 }}>
                  <span>{p.name}</span>
                  <input
                    type={paramInputKind(p.kind)}
                    value={typeof (values[sig.endpoint] ?? {})[p.name] === "boolean" ? undefined : String((values[sig.endpoint] ?? {})[p.name] ?? "")}
                    checked={p.kind === "boolean" ? (values[sig.endpoint]?.[p.name] ?? false) === true : undefined}
                    onChange={(e) =>
                      setValues((v) => ({
                        ...v,
                        [sig.endpoint]: {
                          ...v[sig.endpoint],
                          [p.name]:
                            p.kind === "boolean"
                              ? (e.target as HTMLInputElement).checked
                              : (e.target as HTMLInputElement).value,
                        },
                      }))
                    }
                  />
                </label>
              ))}
              {sig.params.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <button onClick={() => evaluate(sig.endpoint, sig.fn)}>{t("scr.calc_run")}</button>
                </div>
              )}
              {outcomes[sig.endpoint] && (
                <pre
                  style={{
                    whiteSpace: "pre-wrap",
                    marginTop: 8,
                    color: outcomes[sig.endpoint].ok ? "#9be29b" : "#ff9b9b",
                  }}
                >
                  {outcomes[sig.endpoint].text}
                </pre>
              )}
            </fieldset>
          ))}
        </>
      )}
    </div>
  );
}
