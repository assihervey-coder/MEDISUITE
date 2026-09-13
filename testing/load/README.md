# Charge k6 — MEDISUITE (v0.12)

Instruments de charge verrouillés ; l'exécution avec un trafic réaliste CHU
est un livrable **d'exécution terrain** (jalons R6-R7, plan de validation).
Seuil EGSP : **p95 ≤ 2 000 ms** (dossier CE §4, reprise du banc
`docs/BENCHMARK-GPU.md`).

| Script | Profil | Cible |
|---|---|---|
| `k6-smoke.js` | 5 VU × 30 s | santé `/health/all` + chemin critique auth |
| `k6-stress.js` | 10→50→100 VU en paliers | santé + registry + patients (si `TOKEN`) |

Usage :

```bash
k6 run -e BASE_URL=http://localhost:8000 testing/load/k6-smoke.js
k6 run -e BASE_URL=https://staging.medisuite.ci -e TOKEN=<jwt> testing/load/k6-stress.js
```

CI : workflow `ci-load.yml` (déclenchement manuel, image docker `grafana/k6`,
BASE_URL fourni en input — jamais bloquant pour une release).

**Éthique** : aucune donnée patient réelle — les jeux de charge sont les
comptes de démonstration seedés ou des lectures publiques/health. Les
mesures sont archivées comme artefacts CI, jamais comme preuves cliniques.
