import { useEffect, useState } from "react";
import { api } from "../../services/api";

/** Étiquette réglementaire (MDR Annexe I §23.2, Règlement UDI 2019/320).
 *  Source de vérité : GET /api/v1/about (api-gateway, public).
 *  Repli hors-ligne : valeurs de build (VITE_APP_VERSION) + avertissement. */
interface Labeling {
  produit: string;
  fabricant: string;
  version: string;
  commit?: string;
  date_liberation: string;
  basic_udi_di: string;
  basic_udi_di_statut?: string;
  udi_eid: string;
  classe_mdr: string;
  marquage_ce: boolean;
  marquage_ce_texte: string;
  destinataires?: string;
  ifu?: string[];
  symboles?: Array<{ symbole: string; signification: string }>;
  avertissement?: string;
}

const FALLBACK: Labeling = {
  produit: "MEDISUITE — Plateforme d'aide à la décision clinique",
  fabricant: "ASSI Herve — Abidjan, Côte d'Ivoire",
  version: import.meta.env.VITE_APP_VERSION ?? "v0.6.0",
  date_liberation: "2026-09-14",
  basic_udi_di: "MEDISUITE-PLTF-AIDE-DECISION",
  udi_eid: "non attribué (jalon R8)",
  classe_mdr: "IIb (règle 11, Annexe VIII MDR 2017/745)",
  marquage_ce: false,
  marquage_ce_texte:
    "NON CE — usage clinique interdit hors cadre pilote recherche",
};

export default function About() {
  const [label, setLabel] = useState<Labeling | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    api
      .get<Labeling>("/api/v1/about")
      .then((r) => setLabel(r))
      .catch(() => {
        setLabel(FALLBACK);
        setOffline(true);
      });
  }, []);

  if (!label) return <div><h2>ℹ️ À propos</h2><p className="note">chargement…</p></div>;

  return (
    <div>
      <h2>ℹ️ À propos — étiquetage UDI</h2>
      {offline && (
        <p className="error">
          api-gateway injoignable — étiquette de repli (build). La version
          affichée ici n&apos;est PAS la version réglementaire.
        </p>
      )}

      <div className="cards" style={{ marginBottom: 18 }}>
        <div className="card">
          <h3>Identification produit</h3>
          <p style={{ margin: 0 }}>{label.produit}</p>
          <p className="kpi" style={{ fontSize: 20 }}>{label.version}</p>
          <p className="sub">
            commit : {label.commit ?? "inconnu"} · libéré le{" "}
            {label.date_liberation}
          </p>
        </div>
        <div className="card">
          <h3>Identification réglementaire</h3>
          <p style={{ margin: 0 }}>
            Basic UDI-DI : <code>{label.basic_udi_di}</code>
          </p>
          {label.basic_udi_di_statut && (
            <p className="sub">{label.basic_udi_di_statut}</p>
          )}
          <p style={{ margin: "6px 0 0" }}>UDI-EID : {label.udi_eid}</p>
          <p className="sub">Classe : {label.classe_mdr}</p>
        </div>
        <div className="card">
          <h3>Marquage CE</h3>
          <p>
            <span className="badge critical">
              {label.marquage_ce ? "CE" : "❌ NON CE"}
            </span>
          </p>
          <p className="sub">{label.marquage_ce_texte}</p>
        </div>
        <div className="card">
          <h3>Fabricant</h3>
          <p style={{ margin: 0 }}>{label.fabricant}</p>
          {label.destinataires && (
            <p className="sub">Destinataires : {label.destinataires}</p>
          )}
        </div>
      </div>

      <h3 style={{ marginBottom: 6 }}>Notice d&apos;utilisation (IFU)</h3>
      <p className="note">
        IFU électroniques fournies avec la release (dossier <code>ifu/</code>),
        obligatoires avant usage :
      </p>
      <p>
        {(label.ifu ??
          ["IFU-clinicien", "IFU-technicien", "IFU-administrateur", "IFU-patient"]).map(
          (f) => (
            <code key={f} style={{ marginRight: 8 }}>{f}</code>
          ),
        )}
      </p>

      {!!label.symboles?.length && (
        <>
          <h3 style={{ marginBottom: 6 }}>Symboles</h3>
          <table>
            <thead>
              <tr><th>Symbole / texte</th><th>Signification</th></tr>
            </thead>
            <tbody>
              {label.symboles.map((s) => (
                <tr key={s.symbole}>
                  <td>{s.symbole}</td>
                  <td>{s.signification}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {label.avertissement && (
        <p style={{ marginTop: 14 }} className="badge warn">
          {label.avertissement}
        </p>
      )}
    </div>
  );
}
