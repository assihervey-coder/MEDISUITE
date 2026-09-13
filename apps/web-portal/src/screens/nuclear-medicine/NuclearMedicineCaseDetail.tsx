/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Médecine nucléaire · Fiche cas clinique.
 *  Route : /module/nuclear-medicine/cas/:caseId · service : nuclear-medicine-service (module 22).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import CaseDetailScreen from "../templates/CaseDetailScreen";
import { screenById } from "../registry.generated";

export default function NuclearMedicineCaseDetail() {
  return <CaseDetailScreen screen={screenById("nuclear-medicine:detail")!} />;
}
