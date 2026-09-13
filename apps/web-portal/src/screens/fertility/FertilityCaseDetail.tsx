/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Fertilité · Fiche cas clinique.
 *  Route : /module/fertility/cas/:caseId · service : fertility-service (module 12).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function FertilityCaseDetail() {
  return <CaseDetailScreen screen={screenById("fertility:detail")!} />;
}
