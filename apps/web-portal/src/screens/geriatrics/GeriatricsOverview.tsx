/** GÉNÉRÉ par tools/generate_screens.py (v0.14) — écran fin : Gériatrie · Vue d'ensemble du module.
 *  Route : /module/geriatrics · service : geriatrics-service (module 25).
 *  Régénérer : `make screens` — ne pas éditer à la main. */
import OverviewScreen from "../templates/OverviewScreen";
import { screenById } from "../registry.generated";

export default function GeriatricsOverview() {
  return <OverviewScreen screen={screenById("geriatrics:overview")!} />;
}
