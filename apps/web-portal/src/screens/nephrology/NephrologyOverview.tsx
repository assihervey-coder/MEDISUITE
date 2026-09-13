/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Néphrologie · Vue d'ensemble du module.
 *  Route : /module/nephrology · service : nephrology-service (module 16).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function NephrologyOverview() {
  return <OverviewScreen screen={screenById("nephrology:overview")!} />;
}
