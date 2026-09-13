/** Gabarit « vue d'ensemble » des écrans fins (v0.14) — KPIs réels dérivés
 *  des cas du service, scores disponibles, tabs vers les 3 écrans sœurs.
 *  Données vivantes (module-info + liste des cas) — rien en cache offline. */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../services/api";
import { computeKpis, siblingRoute } from "../logic";
import type { CaseRow, ScreenDef } from "../types";
import { useI18n } from "../../i18n/i18n";
import type { MsgKey } from "../../i18n/resolve";

export default function OverviewScreen({ screen }: { screen: ScreenDef }) {
  const { t } = useI18n();
  const [cases, setCases] = useState<CaseRow[] | null>(null);
  const [scores, setScores] = useState<string[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<{ scores: string[] }>(`/api/specialty/${screen.urlSlug}/module-info`)
      .then((i) => setScores(i.scores))
      .catch(() => setScores(screen.scores));
    api
      .get<CaseRow[]>(`/api/specialty/${screen.urlSlug}/api/v1/cases`)
      .then(setCases)
      .catch((e) => {
        setCases([]);
        setError(e.message);
      });
  }, [screen.urlSlug, screen.scores]);

  const kpis = computeKpis(cases ?? []);

  return (
    <div>
      <nav aria-label="breadcrumb" className="note">
        <Link to={siblingRoute(screen, "overview")}>
          {screen.icon} {t(`mod.${screen.slug}` as MsgKey)}
        </Link>
        {" · "}
        {t("scr.overview")}
      </nav>
      <h2>
        {screen.icon} {t(`mod.${screen.slug}` as MsgKey)} — {t("scr.overview")}
      </h2>
      <p className="note">
        {t("scr.module_no")} {screen.moduleNo.toString().padStart(2, "0")} · {screen.service}
      </p>
      {error && (
        <p className="error">
          {t("scr.unreachable")} ({error})
        </p>
      )}

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", margin: "12px 0" }}>
        {[
          { k: "scr.kpi_total" as MsgKey, v: kpis.total },
          { k: "scr.kpi_active" as MsgKey, v: kpis.actifs },
          { k: "scr.kpi_closed" as MsgKey, v: kpis.clos },
          { k: "scr.kpi_severe" as MsgKey, v: kpis.severe },
        ].map(({ k, v }) => (
          <div
            key={k}
            style={{
              border: "1px solid rgba(255,255,255,.2)",
              borderRadius: 8,
              padding: "8px 16px",
              minWidth: 110,
            }}
          >
            <div style={{ fontSize: 26, fontWeight: 700 }}>{v}</div>
            <div style={{ fontSize: 13, color: "#a8c4dc" }}>{t(k)}</div>
          </div>
        ))}
      </div>

      <p>
        <strong>{t("scr.scores_available")}</strong> :{" "}
        {(scores ?? []).length === 0 ? (
          <span className="note">{t("scr.no_scores")}</span>
        ) : (
          (scores ?? []).map((s) => (
            <code key={s} style={{ marginRight: 6 }}>
              {s}
            </code>
          ))
        )}
      </p>

      <p style={{ display: "flex", gap: 12, marginTop: 16 }}>
        <Link className="badge" to={siblingRoute(screen, "cas")}>
          {t("scr.cas")} →
        </Link>
        <Link className="badge" to={siblingRoute(screen, "ia")}>
          {t("scr.ia")} →
        </Link>
      </p>
    </div>
  );
}
