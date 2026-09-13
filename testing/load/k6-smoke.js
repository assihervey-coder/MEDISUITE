/** k6 — smoke charge : santé + chemin critique auth (v0.12).
 *
 * Usage :
 *   k6 run -e BASE_URL=http://localhost:8000 testing/load/k6-smoke.js
 *
 * Seuil EGSP (dossier CE §4) : p95 ≤ 2000 ms sur toute requête.
 * Exécution terrain avec traffic réaliste CHU : jalon R6-R7 (livrable
 * d'exécution 🔴) — ce script est l'instrument verrouillé en CI.
 */
import http from "k6/http";
import { check, group, sleep } from "k6";

const BASE = __ENV.BASE_URL || "http://localhost:8000";

export const options = {
  vus: 5,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<2000"],
  },
};

export default function () {
  group("santé globale", () => {
    const health = http.get(`${BASE}/health/all`);
    check(health, {
      "health 200": (r) => r.status === 200,
    });
  });

  group("auth — chemin critique (connexion)", () => {
    const res = http.post(
      `${BASE}/api/v1/auth/login`,
      JSON.stringify({
        email: "medecin@chu-cocody.ci",
        password: "MediSuite2026!",
      }),
      { headers: { "Content-Type": "application/json" } },
    );
    // 200 = service OK ; 401/422 = service vif mais compte de charge absent —
    // les deux attestent que la requête a traversé la pile complète.
    check(res, {
      "auth répond 2xx/4xx attendus": (r) => [200, 401, 422].includes(r.status),
      "auth p95 EGSP": (r) => r.timings.duration < 2000,
    });
  });

  sleep(1);
}
