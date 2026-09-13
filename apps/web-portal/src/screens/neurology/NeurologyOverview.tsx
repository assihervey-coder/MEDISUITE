/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Neurologie · Vue d'ensemble du module.
 *  Route : /module/neurology · service : neurology-service (module 13).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function NeurologyOverview() {
  return <OverviewScreen screen={screenById("neurology:overview")!} />;
}
