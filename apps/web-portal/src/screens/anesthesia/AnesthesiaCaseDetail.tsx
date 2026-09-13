/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Anesthésie-Réanimation · Fiche cas clinique.
 *  Route : /module/anesthesia/cas/:caseId · service : anesthesia-service (module 24).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function AnesthesiaCaseDetail() {
  return <CaseDetailScreen screen={screenById("anesthesia:detail")!} />;
}
