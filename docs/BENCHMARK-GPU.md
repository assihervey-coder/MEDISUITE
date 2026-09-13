# Banc de performance d'inférence — méthodologie et référentiels (v0.5)

> Outil : `tools/bench/bench_fusion.py` (stdlib + numpy/torch). Critère EGSP
> (dossier CE §4) : **latence d'inférence p95 ≤ 2 s** par requête de fusion.
> Les référentiels CPU ci-dessous sont des mesures réelles reproductibles
> (`--seed 42`) ; les mesures GPU CHU (K8s time-slicing) seront ajoutées au
> jalon R4/R5 avec le même outil — comparabilité garantie.

## 1. Méthodologie

| Élément | Choix | Justification |
|---|---|---|
| Charge | payload synthétique : imagerie 2D 32×32 + tabulaire 6 paramètres | représentatif d'une requête FusionViewer (2 modalités) ; reproductible sans PACS |
| Réchauffement | 20 requêtes hors mesure | amortit JIT/caches/allocations |
| Horloge | `perf_counter_ns` autour de l'appel complet | inclut encodage + fusion + tête, comme en production |
| Scénario dégradé | `--missing-ratio 0.3` (30 % sans imagerie) | valide le chemin modalités manquantes (ADR-0018) |
| Modèle torch | fit 30 epochs avant mesure | performance représentative d'un modèle déployé, pas d'un modèle vierge |
| Verdict | p95 ≤ 2000 ms | seuil EGSP ; la CI fait échouer le script sinon (exit 1) |
| Seed | 42 partout | mesures bit-reproductibles (données et ordre d'allocation) |

## 2. Référentiels mesurés (2026-09-14, module 8 cardiology, seed 42)

| Scénario | Backend | Device | p50 | p95 | p99 | Débit | Verdict |
|---|---|---|---|---|---|---|---|
| 500 req, 2 modalités | numpy | CPU | 0,28 ms | **0,32 ms** | 0,37 ms | 3 535 req/s | PASS |
| 300 req, 2 modalités | torch 2.14+cpu | CPU | 0,67 ms | **0,79 ms** | 0,85 ms | 1 481 req/s | PASS |
| 300 req, 30 % manquantes | torch 2.14+cpu | CPU | ~0,50 ms | **0,60 ms** | ~0,70 ms | 1 940 req/s | PASS |

Constats : le socle NumPy reste ~2× plus rapide que torch/CPU sur de petites
tensions d_model (32) — cohérent avec l'ADR-0022 (numpy par défaut, torch
pour l'entraînement) ; le chemin dégradé est *plus* rapide qu'une requête
complète (une modalité en moins à encoder) et reste validé.

**Interprétation pour le dimensionnement GPU** : au p95 CPU mesuré (0,79 ms),
un service d'inférence mono-réplique absorbe déjà ~1 400 req/s — la fenêtre
thérapeutique (secondes) n'est jamais le facteur limitant à l'échelle CHU
pilote. Le GPU (time-slicing ×2, K8s GPU v0.4) devient pertinent pour les
charges lourdes (segmentation 3D, volumes DICOM complets), pas pour la
fusion tabulaire+2D — décision d'orchestration documentée dans
`docs/K8S-GPU.md` §4.

## 3. Protocole GPU CHU (à exécuter sur le cluster, jalon R4/R5)

```bash
kubectl -n medisuite run bench --rm -it \
  --image=ghcr.io/assihervey-coder/medisuite/bench:0.5.0 -- \
  python3 tools/bench/bench_fusion.py --backend torch --requests 1000 \
  -o /results/bench_gpu.json
```

Points à documenter lors de la campagne GPU :
1. device réel (`cuda`), modèle GPU, driver CUDA, time-slicing actif ;
2. p95 mesuré **avec et sans co-tenant GPU** (mesure de l'interférence du
   time-slicing — compromis assumé de l'ADR K8s GPU) ;
3. p95 en charge concurrente (k6/JMeter contre le Service :8022, 50 VUs) —
   le banc actuel mesure la latence unitaire, pas la saturation ;
4. dérive p95 après montée de version de modèle (boucle PMS).

## 4. Intégration CI et PMS

- CI : `python3 tools/bench/bench_fusion.py --backend numpy --requests 200`
  (rapide, sans GPU) — garde-fou contre toute régression de performance du
  socle ; échec si p95 > 2 s (improbable à ce niveau : le critère protège
  plutôt d'une régression d'architecture).
- PMS : le p95 OTel en production (`http.duration_ms`, job Prometheus `otel`)
  est l'indicateur réel de surveillance (revue mensuelle — `07-pms-vigilance.md`) ;
  le banc sert de référence de comparaison à chaud.

## 5. Fichiers de résultats

Les JSON bruts sont versionnés dans `tools/bench/` :
`resultats_cpu_numpy.json`, `resultats_cpu_torch.json`,
`resultats_cpu_torch_missing.json` (métadonnées complètes : date, device,
seed, payload, verdict).
