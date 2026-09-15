/** Gabarit « assistance IA » des écrans fins (v0.14) — transparence du module
 *  IA : tâche, modalités, politique des modalités manquantes (ADR-0018),
 *  explicabilité (ADR-0015), features attendues, spec de label — avec
 *  AVERTISSEMENT permanent de validité clinique (🔴 R6-R8, verrou M+18)
 *  rendu par le bandeau de gouvernance partagé. */
import { Link } from "react-router-dom";
import { siblingRoute } from "../logic";
import type { ScreenDef } from "../types";
import GovernanceBanner from "../../features/governance/GovernanceBanner";
import { useI18n } from "../../i18n/i18n";
import type { MsgKey } from "../../i18n/resolve";

export default function AiAssistScreen({ screen }: { screen: ScreenDef }) {
  const { t } = useI18n();
  const ai = screen.ai;
  const hasImaging = ai.modalities.some((m) => m.startsWith("imaging"));

  return (
    <div>
      <nav aria-label="breadcrumb" className="note">
        <Link to={siblingRoute(screen, "overview")}>
          {screen.icon} {t(`mod.${screen.slug}` as MsgKey)}
        </Link>
        {" · "}
        {t("scr.ia")}
      </nav>
      <h2>
        {screen.icon} {t(`mod.${screen.slug}` as MsgKey)} — {t("scr.ia")}
      </h2>

      <GovernanceBanner text={t("scr.ai_banner")} withCountdown={false} compact testId="governance-banner-ai" />
      <p className="note">{t("scr.ai_consent")}</p>

      <table>
        <tbody>
          <tr>
            <th>{t("scr.ai_task")}</th>
            <td>
              <code>{ai.task}</code> ({t("scr.ai_label")} : <code>{ai.labelTask}</code>
              {ai.labelNom !== "" && (
                <>
                  {" · "}
                  <code>{ai.labelNom}</code>
                </>
              )}
              {ai.classes.length > 0 && (
                <>
                  {" · "}
                  {ai.classes.map((c) => (
                    <code key={c} style={{ marginRight: 6 }}>{c}</code>
                  ))}
                </>
              )}
              )
            </td>
          </tr>
          <tr>
            <th>{t("scr.ai_modalities")}</th>
            <td>
              {ai.modalities.map((m) => (
                <code key={m} style={{ marginRight: 6 }}>{m}</code>
              ))}
              {ai.modalities.length === 0 && <span className="note">{t("scr.no_scores")}</span>}
            </td>
          </tr>
          <tr>
            <th>ADR-0018</th>
            <td>
              {t("scr.ai_missing")} : <code>{ai.missingPolicy}</code>
            </td>
          </tr>
          <tr>
            <th>ADR-0019</th>
            <td>{ai.sharedTrunk ? "trunk partagé (multi-tâches)" : "têtes indépendantes"}</td>
          </tr>
          <tr>
            <th>ADR-0015</th>
            <td>
              {t("scr.ai_explain")} :{" "}
              {ai.explainability.map((e) => (
                <code key={e} style={{ marginRight: 6 }}>{e}</code>
              ))}
              {ai.explainability.length === 0 && "—"}
            </td>
          </tr>
          <tr>
            <th>{t("scr.ai_features")}</th>
            <td>
              {ai.features.map((f) => (
                <code key={f.name} style={{ marginRight: 8 }}>
                  {f.name} ∈ [{f.lo}, {f.hi}]
                </code>
              ))}
              {ai.features.length === 0 && "—"}
            </td>
          </tr>
        </tbody>
      </table>

      {hasImaging && (
        <p style={{ marginTop: 14 }}>
          <Link className="badge" to="/multimodal">
            {t("scr.ai_viewer")} →
          </Link>
        </p>
      )}
    </div>
  );
}
