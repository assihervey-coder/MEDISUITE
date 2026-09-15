/**
 * Bandeau de gouvernance partagé — verrou investigation M+18 (v0.14).
 *
 * Un seul composant pour TOUTES les surfaces IA du portail : /decision
 * (TropiRAG), /epidemiologie (signaux d'éclosion), /study (promoteur) et le
 * gabarit des 28 écrans AiAssist (via la clé i18n existante scr.ai_banner).
 * Non dismissible : un avertissement réglementaire ne se ferme pas.
 */
import type { CSSProperties } from "react";
import {
  BANNER_TEXT,
  countdownLabel,
  PROTOCOL,
} from "./investigation";

const bannerStyle: CSSProperties = {
  border: "1px solid rgba(178, 34, 34, 0.45)",
  background: "rgba(178, 34, 34, 0.08)",
  borderRadius: 8,
  padding: "10px 14px",
  margin: "8px 0",
};

const stampStyle: CSSProperties = {
  ...bannerStyle,
  background: "rgba(178, 34, 34, 0.05)",
  padding: "6px 10px",
  fontSize: 12.5,
};

export default function GovernanceBanner({
  text = BANNER_TEXT,
  withCountdown = true,
  compact = false,
  testId = "governance-banner",
}: {
  /** Texte réglementaire — par défaut la phrase de référence ; les écrans
   * i18n passent leur clé traduite (scr.ai_banner, 4 langues). */
  text?: string;
  /** Ajoute la ligne de compte à rebours M+18 (phase active + J-restants). */
  withCountdown?: boolean;
  /** Variante compacte (écrans spécialisés, sous-bandeaux). */
  compact?: boolean;
  testId?: string;
}) {
  return (
    <div
      className={compact ? "note" : "banner warn"}
      role="alert"
      style={{ ...bannerStyle, ...(compact ? stampStyle : {}) }}
      data-testid={testId}
    >
      <strong>🔴 {text}</strong>
      {withCountdown && (
        <div style={{ marginTop: 4, fontSize: 12.5, opacity: 0.9 }}>
          ⏳ {countdownLabel()} · protocole {PROTOCOL} (MDR Annexe XV / ISO 14155)
        </div>
      )}
    </div>
  );
}

/** Tampon par-sortie — apposé sous chaque restitution IA (résultat TropiRAG,
 * synthèse mesh). Version inline, sans compte à rebours. */
export function OutputStamp({ testId = "governance-stamp" }: { testId?: string }) {
  return (
    <div style={stampStyle} data-testid={testId}>
      🔬 Sortie d'investigation — non décisionnelle : usage à titre de recherche
      uniquement (interdiction reprise dans le bloc <code>governance</code> de
      l'API ; tentative de matérialisation → 451).
    </div>
  );
}
