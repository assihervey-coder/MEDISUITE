/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Diabétologie · Vue d'ensemble du module.
 *  Route : /module/diabetes · service : diabetes-service (module 06).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function DiabetesOverview() {
  return <OverviewScreen screen={screenById("diabetes:overview")!} />;
}
