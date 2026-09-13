/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Obstétrique · Vue d'ensemble du module.
 *  Route : /module/obstetrics · service : obstetrics-service (module 10).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function ObstetricsOverview() {
  return <OverviewScreen screen={screenById("obstetrics:overview")!} />;
}
