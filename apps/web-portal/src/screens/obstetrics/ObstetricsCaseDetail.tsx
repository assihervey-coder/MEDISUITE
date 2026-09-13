/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Obstétrique · Fiche cas clinique.
 *  Route : /module/obstetrics/cas/:caseId · service : obstetrics-service (module 10).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function ObstetricsCaseDetail() {
  return <CaseDetailScreen screen={screenById("obstetrics:detail")!} />;
}
