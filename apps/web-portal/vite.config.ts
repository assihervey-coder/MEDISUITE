import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Proxy dev : /api/auth → :8001, etc. En prod, l'api-gateway (:8000) route tout.
// Chaque préfixe /api/{service} est retiré : les microservices servent /api/v1/...
const strip = (prefix: string) => (p: string) => p.replace(new RegExp(`^${prefix}`), "");
const proxy: Record<string, { target: string; rewrite?: (p: string) => string }> = {
  "/api/auth": { target: "http://localhost:8001", rewrite: strip("/api/auth") },
  "/api/patients": { target: "http://localhost:8002", rewrite: strip("/api/patients") },
  "/api/imaging": { target: "http://localhost:8003", rewrite: strip("/api/imaging") },
  "/api/lab": { target: "http://localhost:8004", rewrite: strip("/api/lab") },
  "/api/multimodal": { target: "http://localhost:8302", rewrite: strip("/api/multimodal") },
  "/api/explainability": { target: "http://localhost:8303", rewrite: strip("/api/explainability") },
  "/api/audit": { target: "http://localhost:8202", rewrite: strip("/api/audit") },
  "/api/analytics": { target: "http://localhost:8204", rewrite: strip("/api/analytics") },
  // eCRF (v0.7) : le préfixe /api/ecrf est retiré comme le fait l'api-gateway
  "/api/ecrf": { target: "http://localhost:8205", rewrite: strip("/api/ecrf") },
  // Spécialités (v0.5) : /api/specialty/{module} → service dédié 8100-8123
  "/api/specialty/emergency": { target: "http://localhost:8123", rewrite: strip("/api/specialty/emergency") },
  "/api/specialty/oncology": { target: "http://localhost:8100", rewrite: strip("/api/specialty/oncology") },
  // Étiquetage UDI public servi par l'api-gateway
  "/api/v1/about": { target: "http://localhost:8000" },
};

export default defineConfig({
  plugins: [react()],
  server: { port: 3000, host: true, allowedHosts: true, proxy },
  // vitest : uniquement les tests unitaires du src — les parcours e2e
  // Playwright (e2e/*.spec.ts) ont leur runner dédié (npx playwright test).
  test: { environment: "node", exclude: ["e2e/**", "**/node_modules/**"] },
});
