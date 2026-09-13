# Télémétrie OpenTelemetry (v0.4)

Chaque requête HTTP des 38 services MEDISUITE produit désormais un **span
OpenTelemetry** exporté au format **OTLP/HTTP JSON** vers un collecteur
`otel/opentelemetry-collector-contrib`. Objectif clinique : reconstruire le
parcours complet d'une demande patient (gateway → service métier → PACS →
référentiel FHIR) pour la traçabilité IEC 81001-5-1 et la recherche de
goulots en charge hospitalière réelle.

## 1. Architecture

```
┌───────────────────────┐  HTTP + traceparent (W3C)  ┌──────────────┐
│ api-gateway :8000     │───────────────────────────▶│ auth-service │
│ middleware OTel       │◀───────────────────────────│ (poursuit la │
│ span + export batch   │      traceparent réponse   │  même trace) │
└──────────┬────────────┘                            └──────────────┘
           │ POST OTLP/HTTP JSON (batch, thread de fond)
           ▼
┌───────────────────────┐        ┌────────────────────────────┐
│ otel-collector :4318  │───────▶│ Prometheus :8889 (métriques│
│ batch + resource +    │        │ de traces, job "otel")     │
│ memory_limiter        │        └────────────────────────────┘
└──────────┬────────────┘
           ▼ logs debug (docker logs otel-collector)
```

## 2. Ce qui est instrumenté (v0.4)

| Élément | Implémentation |
|---|---|
| **Propagation W3C** | `traceparent` lu sur la requête entrante, réémis sur la réponse (`00-<32 hex>-<16 hex>-<flags>`) ; headers invalides ignorés sans erreur |
| **Span serveur** | `HTTP <méthode> <route>` avec `http.method`, `http.route`, `http.status_code`, `http.duration_ms`, `medisuite.request_id` |
| **Corrélation logs** | `X-Request-ID` reste présent et est copié en attribut de span |
| **Export** | OTLP/HTTP JSON (`/v1/traces`), lots de 64+ spans, thread daemon, tampon circulaire 2 048 spans (overflow → `dropped` compté) |
| **Sans collecteur** | export no-op : les spans restent consultables dans le tampon local (`Tracer.snapshot()`) — aucun ralentissement, aucune exception |
| **Échec réseau** | le thread d'export back-off silencieusement (×4) — la télémétrie ne doit jamais dégrader le soin |

## 3. Configuration

Variables d'environnement (déjà injectées par `docker-compose.minimal.yml`) :

```bash
MEDISUITE_OTEL_ENDPOINT=http://otel-collector:4318/v1/traces
```

En K8s GPU (`infrastructure/kubernetes/gpu/fusion-inference.yaml`) :

```bash
MEDISUITE_OTEL_ENDPOINT=http://otel-collector.observability.svc:4318/v1/traces
MEDISUITE_TORCH_DEVICE=cuda
```

Démarrage local :

```bash
docker compose -f local-deployment/docker-compose.minimal.yml up otel-collector
curl -s http://localhost:8889/metrics | head   # métriques de traces exposées
```

## 4. Point d'instrumentation unique

Le middleware vit dans `medisuite_core.http.create_service_app` — la fabrique
utilisée par les 38 services. **Aucun service à modifier** : toute app créée
par la fabrique est instrumentée d'office, ce qui garantit l'homogénéité
(contrat de service MEDISUITE).

```python
from medisuite_core.http import create_service_app
app = create_service_app("cardiology-service", "Cardiologie", "…")
# → spans OTel automatiques sur toutes les routes
```

## 5. Limites connues

- **Métriques applicatives** : seules les métriques dérivées des traces sont
  exposées via le collector ; les compteurs métier (ordonnances, résultats
  critiques) restent sur les `/metrics` FastAPI existants — unification
  prévue v1.0 avec le SDK OTel officiel quand l'emprise mémoire le permettra.
- **Sampling (ADR-0025, v0.8)** : head sampling **déterministe parent-based**
  — décision du parent W3C honorée, sinon ratio déterministe sur le
  trace_id (`MEDISUITE_OTEL_SAMPLING_RATIO`, défaut **1.0** pendant
  l'investigation R6 ; 0.1 recommandé en production courante) ; spans en
  erreur **toujours** exportés ; probes `/health`, `/ready`, `/metrics`
  sans span ; décision propagée en aval (flags `01`/`00`) et mesurable
  (`snapshot() → sampling_ratio/sampling_dropped`). Un tail sampling au
  collecteur reste réévaluable quand le volume réel CHU sera mesuré.
- **Traces cross-service partielles** : la propagation s'appuie sur les
  appels HTTP entrants ; les appels sortants effectués hors middleware
  (ex. `HapiClient` interne) créent des traces distinctes tant que les
  clients ne propagent pas le header — feuille de route v1.0.
- **OTLP JSON, pas protobuf** : échange de compacité contre zéro dépendance
  (contrainte « stdlib d'abord ») ; le collecteur décode nativement les deux.

## 6. Tests

`test_traceparent_roundtrip` (format/parse + 5 headers invalides),
`test_middleware_creates_span_and_propagates` (span enregistré + trace
poursuivie de bout en bout), `test_otlp_export_payload` (payload OTLP JSON
conforme : `resourceSpans → scopeSpans → spans`, ids W3C, statut erreur)
et le lot ADR-0025 (`test_noise_routes_produce_no_span`,
`test_sampling_root_ratio_deterministic`, `test_sampling_parent_based`,
`test_sampling_always_on_errors`, `test_sampling_unsampled_propagates_flags_00`,
`test_sampling_ratio_env_fail_open`) — 21/21 verts sur integration-service.
