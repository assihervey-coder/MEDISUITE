/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Pédiatrie · Vue d'ensemble du module.
 *  Route : /module/pediatrics · service : pediatrics-service (module 15).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function PediatricsOverview() {
  return <OverviewScreen screen={screenById("pediatrics:overview")!} />;
}
