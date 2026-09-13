/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Tumeurs · Vue d'ensemble du module.
 *  Route : /module/tumor · service : tumor-service (module 04).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function TumorOverview() {
  return <OverviewScreen screen={screenById("tumor:overview")!} />;
}
