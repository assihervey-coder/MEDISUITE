/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : ORL · Fiche cas clinique.
 *  Route : /module/ent/cas/:caseId · service : ent-service (module 19).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function EntCaseDetail() {
  return <CaseDetailScreen screen={screenById("ent:detail")!} />;
}
