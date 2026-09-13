/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Anesthésie-Réanimation · Vue d'ensemble du module.
 *  Route : /module/anesthesia · service : anesthesia-service (module 24).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function AnesthesiaOverview() {
  return <OverviewScreen screen={screenById("anesthesia:overview")!} />;
}
