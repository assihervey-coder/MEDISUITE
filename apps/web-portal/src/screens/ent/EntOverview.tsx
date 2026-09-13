/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : ORL · Vue d'ensemble du module.
 *  Route : /module/ent · service : ent-service (module 19).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function EntOverview() {
  return <OverviewScreen screen={screenById("ent:overview")!} />;
}
