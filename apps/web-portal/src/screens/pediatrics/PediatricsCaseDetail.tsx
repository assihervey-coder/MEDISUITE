/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pédiatrie · Fiche cas clinique.
 *  Route : /module/pediatrics/cas/:caseId · service : pediatrics-service (module 15).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function PediatricsCaseDetail() {
  return <CaseDetailScreen screen={screenById("pediatrics:detail")!} />;
}
