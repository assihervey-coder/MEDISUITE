# Export DHIS2 — MSP-CI (V1.2)

> Intégration du système national d'information sanitaire DHIS2
> (District Health Information System 2) — Ministère de la Santé Publique
> et de l'Hygiène, Côte d'Ivoire.

## Principe

TropiRAG exporte des **indicateurs de surveillance agrégés** dérivés
exclusivement des analyses déterministes persistées (table `analyses`).
Aucune IA ne participe au comptage : chaque valeur est auditable ligne à
ligne (règle matchée, différentiel, urgence, sévérité).

```
analyses persistées → Dhis2Mapper (compteurs) → DataValue(s)
    → Exporter (JSON dataValueSets / CSV / ADX 2.0 XML)
    → File offline (runtime/state/dhis2_queue.json)
    → Transport (POST /api/dataValueSets — uniquement si configuré)
```

**Sécurité réseau** : aucun envoi implicite. Le mode par défaut est
`offline_queue` : les payloads attendent en local jusqu'à ce que le serveur
et les identifiants du MSP-CI soient configurés.

## Utilisation

### API

| Route | Description |
|---|---|
| `POST /api/v1/export/dhis2` | Export de la période (défaut : semaine ISO en cours) |
| `GET /api/v1/export/dhis2/status` | État de la file d'attente offline |
| `POST /api/v1/export/dhis2/push` | Tentative d'envoi de la file (explicite) |

```bash
# Dry-run : compter et rendre le payload sans rien écrire
curl -X POST http://localhost:8000/api/v1/export/dhis2 \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $TROPIRAG_API_KEY" \
     -d '{"period": "2026W37", "format": "adx", "enqueue": false}'

# Mise en file offline (défaut selon la configuration)
curl -X POST http://localhost:8000/api/v1/export/dhis2 -d '{}'
```

Corps accepté : `period` (YYYYWww), `org_unit`, `format`
(`json` | `csv` | `adx`), `enqueue` (true : forcer la file ; false :
dry-run ; absent : suivre la config), `limit_rows`.

### CLI

```bash
python scripts/export_dhis2.py                 # semaine en cours, dry-run
python scripts/export_dhis2.py --period 2026W37
python scripts/export_dhis2.py --enqueue       # mettre en file offline
python scripts/export_dhis2.py --format adx    # rendu ADX 2.0 XML
python scripts/export_dhis2.py --status        # état de la file
python scripts/export_dhis2.py --push          # envoyer la file (si configuré)
```

## Indicateurs exportés

17 éléments de données, mappés dans `configs/integrations/dhis2.yaml` :

| Clé logique | Signification |
|---|---|
| `total_cases` | Cas fièvre+voyage analysés |
| `suspect_malaria` / `suspect_severe_malaria` | Suspicion paludisme / forme sévère |
| `malaria_renal_rrt` | Paludisme avec AKI — épuration extrarénale indiquée |
| `suspect_dengue` / `suspect_severe_dengue` | Suspicion dengue / forme sévère |
| `dengue_peds_critical` | Dengue pédiatrique — soins critiques |
| `suspect_enteric_fever` / `typhoid_xdr` | Typhoïde suspectée / XDR |
| `suspect_yellow_fever` / `suspected_vhf` | Fièvre jaune / alertes MVH |
| `suspect_zika` / `zika_pregnant` | Zika (dont femme enceinte) |
| `scd_fever` / `pregnancy_malaria` | Drépanocytose fébrile / paludisme gestationnel |
| `urgent_cases` / `critical_cases` | Charge de gravité globale |

## Mise en production avec le MSP-CI

1. **Récupérer le dictionnaire de données** : remplacer les UID
   placeholder (`DE-TRPG-…`) de `configs/integrations/dhis2.yaml` par les
   vrais identifiants des éléments de données DHIS2 nationaux — les clés
   logiques restent stables, aucun code à modifier.
2. **Renseigner l'organisation** : `organisation_unit.default` = code de
   la structure de saisie (district / centre de santé).
3. **Configurer le serveur** (une fois le réseau sanitaire établi) :
   ```yaml
   dhis2:
     mode: push
     server:
       base_url: https://dhis2.msp-ci.example/api
       username: tropirag-district
   ```
   Mot de passe : variable d'environnement `TROPIRAG_DHIS2_PASSWORD`
   (jamais dans le fichier).
4. **Vider la file accumulée** : `python scripts/export_dhis2.py --push`
   ou `POST /api/v1/export/dhis2/push`.

## Formats de sortie

- **JSON** `dataValueSets` — format natif de l'API DHIS2
  (`POST /api/dataValueSets`).
- **CSV** — import manuel par l'interface DHIS2 (import/export app).
- **ADX 2.0 XML** (`urn:ihe:iti:adx:2015`) — standard interopérabilité
  sémantique pour les rapports agrégés de santé.

## Dépannage

| Symptôme | Cause / action |
|---|---|
| `payload en file — envoi différé` | Normal : mode `offline_queue`, serveur non configuré |
| `TransportNotConfigured` | `base_url`/`username` absents — voir mise en production |
| File corrompue | Le chargeur repart à vide ; les payloads sont re-productibles depuis la DB |
| Valeurs à zéro absentes | Comportement voulu : DHIS2 n'exige pas les zéros en envoi incrémental |
