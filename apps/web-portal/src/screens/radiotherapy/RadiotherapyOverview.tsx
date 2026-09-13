/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Radiothérapie · Vue d'ensemble du module.
 *  Route : /module/radiotherapy · service : radiotherapy-service (module 23).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function RadiotherapyOverview() {
  return <OverviewScreen screen={screenById("radiotherapy:overview")!} />;
}
