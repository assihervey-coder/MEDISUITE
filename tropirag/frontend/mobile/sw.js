/* TropiRAG Terrain — service worker offline-first.
   Stratégie : cache-first pour la coquille, network-never pour l'API
   (les POST API ne passent jamais par le SW — la file localStorage gère). */
const CACHE = "tropirag-terrain-v1";
const SHELL = [
  "index.html",
  "app.js",
  "manifest.json",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // jamais les appels API (POST/GET dynamiques)
  if (url.pathname.startsWith("/api/") || url.pathname === "/metrics" || e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((hit) =>
      hit ||
      fetch(e.request).then((r) => {
        if (r.ok) {
          const cp = r.clone();
          caches.open(CACHE).then((c) => c.put(e.request, cp));
        }
        return r;
      }).catch(() => caches.match("index.html"))
    )
  );
});
