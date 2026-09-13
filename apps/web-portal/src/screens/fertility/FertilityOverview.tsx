/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Fertilité · Vue d'ensemble du module.
 *  Route : /module/fertility · service : fertility-service (module 12).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function FertilityOverview() {
  return <OverviewScreen screen={screenById("fertility:overview")!} />;
}
