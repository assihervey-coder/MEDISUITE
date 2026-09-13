/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pneumologie · Vue d'ensemble du module.
 *  Route : /module/pneumology · service : pneumology-service (module 09).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function PneumologyOverview() {
  return <OverviewScreen screen={screenById("pneumology:overview")!} />;
}
