/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Urgences · Vue d'ensemble du module.
 *  Route : /module/emergency · service : emergency-service (module 26).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function EmergencyOverview() {
  return <OverviewScreen screen={screenById("emergency:overview")!} />;
}
