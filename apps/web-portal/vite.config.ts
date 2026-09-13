import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Proxy dev : /api/auth → :8001, etc. En prod, l'api-gateway (:8000) route tout.
const proxy: Record<string, { target: string; rewrite?: (p: string) => string }> = {
  "/api/auth": { target: "http://localhost:8001" },
  "/api/patients": { target: "http://localhost:8002" },
  "/api/imaging": { target: "http://localhost:8003" },
  "/api/lab": { target: "http://localhost:8004" },
  "/api/multimodal": { target: "http://localhost:8302" },
  "/api/explainability": { target: "http://localhost:8303" },
  "/api/audit": { target: "http://localhost:8202" },
  "/api/analytics": { target: "http://localhost:8204" },
  // eCRF (v0.7) : le préfixe /api/ecrf est retiré comme le fait l'api-gateway
  "/api/ecrf": {
    target: "http://localhost:8205",
    rewrite: (p) => p.replace(/^\/api\/ecrf/, ""),
  },
};

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy },
  // vitest : uniquement les tests unitaires du src — les parcours e2e
  // Playwright (e2e/*.spec.ts) ont leur runner dédié (npx playwright test).
  test: { environment: "node", exclude: ["e2e/**", "**/node_modules/**"] },
});
