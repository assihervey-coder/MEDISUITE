# Correspondance DHIS2 — MSP-CI / TropiRAG

> **Un seul fichier à éditer : `configs/integrations/dhis2.yaml`**
> Aucune modification de code n'est nécessaire pour la correspondance officielle.

Ce document décrit la procédure de mise en correspondance des indicateurs
TropiRAG avec le dictionnaire de données DHIS2 national du Ministère de la
Santé Publique et de l'Hygiène de Côte d'Ivoire (MSP-CI), puis la bascule
progressive du mode `offline_queue` (par défaut, zéro réseau) vers le mode
`push` (envoi hebdomadaire réel).

---

## 1. Architecture de la correspondance

```
┌──────────────────────┐     clés logiques STABLES     ┌─────────────────────┐
│  TropiRAG (code)      │ ────────────────────────────▶ │  dhis2.yaml          │
│  mapper Dhis2Mapper   │   total_cases, typhoid_xdr…   │  (seul fichier édité)│
└──────────────────────┘                               └──────────┬──────────┘
                                                                  │ de/ds/ou/coc
                                                                  ▼
                                                       ┌─────────────────────┐
                                                       │  DHIS2 national     │
                                                       │  MSP-CI             │
                                                       └─────────────────────┘
```

- Le **code** n'utilise jamais d'UID en dur : il ne connaît que des clés
  logiques (`total_cases`, `suspect_malaria`, `typhoid_xdr`, …).
- Le **YAML** associe chaque clé logique à un UID DHIS2 + un libellé +
  la définition exacte du compte (traçabilité ligne à ligne).
- Toute erreur de correspondance se corrige en éditant le YAML, sans
  redéployer le code.

## 2. Les quatre familles d'UID

| Famille | Préfixe placeholder | Rôle | Où le trouver côté MSP-CI |
|---|---|---|---|
| Éléments de données | `DE-TRPG-*` | Compteur d'indicateur | Maintenance → Data elements (recherche par libellé) |
| Jeu de données | `DS-TRPG-*` | Regroupement « Surveillance hebdomadaire » | Maintenance → Data sets |
| Unité d'organisation | `OU-TRPG-*` | Structure de saisie / district | Maintenance → Organisation units |
| Combo de catégories | `COC-TRPG-*` | Désagrégation (par défaut : aucun) | Maintenance → Category option combos |

**Format UID DHIS2** : 11 caractères, le premier alphabétique, les 10
suivants alphanumériques — `^[A-Za-z][A-Za-z0-9]{10}$`
(ex. `H9nYv2q3LkM`). Le validateur rejette tout autre format.

## 3. Procédure officielle (avec l'équipe SI du MSP-CI)

### Étape 1 — Éléments de données

Pour chacune des 19 lignes de la section `data_elements` :

1. Ouvrir le dictionnaire national DHIS2 (compte de lecture suffit).
2. Rechercher l'indicateur par son libellé (`label`), en vérifiant la
   cohérence avec la `definition` documentée (le compte exact côté TropiRAG).
3. Si l'indicateur existe déjà : recopier son UID dans le champ `de`.
4. S'il n'existe pas : créer l'élément de données avec l'équipe MSP-CI
   (type : nombre entier, agrégation : somme), puis recopier l'UID.

### Étape 2 — Jeu de données

Récupérer (ou créer) le jeu de données de surveillance hebdomadaire qui
recevra les valeurs, renseigner son UID dans `data_sets.weekly_surveillance.ds`,
et y rattacher les 19 éléments de données validés à l'étape 1.

### Étape 3 — Unité d'organisation

- `organisation_unit.default` : UID de la structure de saisie qui exporte
  (l'hôpital/le programme pilote).
- `organisation_unit.units.*` : optionnel — un UID par district sanitaire
  pour la désagrégation géographique future (les 14 districts de premier
  niveau de la Côte d'Ivoire sont pré-remplis avec des placeholders).

### Étape 4 — Validation locale

```bash
python scripts/validate_dhis2_uids.py          # rapport lisible
python scripts/validate_dhis2_uids.py --json   # sortie machine (CI)
python scripts/validate_dhis2_uids.py --strict # exit 1 si incomplet
```

Le validateur confirme : format UID, placeholders restants, complétude du
mapping (19/19), cohérence serveur/mode.

### Étape 5 — Bascule vers l'envoi réel

1. Renseigner `server.base_url` et `server.username`
   (le mot de passe reste dans la variable d'environnement
   `TROPIRAG_DHIS2_PASSWORD`, jamais dans le fichier).
2. Passer `mode: push`.
3. Relancer le validateur — verdict attendu : **PRÊT POUR LE PUSH**.
4. Premiers envois :

```bash
# export de la semaine 2026W37 au format dataValueSets (dry-run visuel)
python scripts/export_dhis2.py --period 2026W37 --format json

# envoi réel de la file d'attente accumulée
python scripts/export_dhis2.py --push
```

> Pendant toute la période de correspondance, le mode `offline_queue`
> accumule les payloads locaux : rien n'est perdu, et l'envoi
> `--push` rattrape l'historique dès que le serveur est configuré.

## 4. Sécurité et auditabilité

- **Zéro réseau par défaut** : le mode `offline_queue` ne tente aucun envoi ;
  le mode `push` n'envoie que sur action explicite (CLI `--push` ou API
  dédiée).
- **Comptes déterministes** : chaque valeur exportée dérive exclusivement des
  analyses du moteur de règles (table `analyses`) — aucune IA ne participe au
  comptage ; l'export est auditable ligne à ligne via le champ `definition`.
- **Tolérance panne réseau** : la file d'attente persiste dans
  `runtime/state/dhis2_queue.json` (redémarrage sûr, max 5 000 entrées).
- **Identifiants** : mot de passe uniquement via variable d'environnement ;
  TLS vérifié par défaut (`verify_tls: true`).

## 5. Fréquence et formats

- Période : hebdomadaire ISO (`YYYYWww`, ex. `2026W37`) — aligné sur la
  routine de surveillance intégrée MSP-CI.
- Formats : `json` (dataValueSets, API DHIS2), `csv` (archivage bureautique),
  `adx` (ADX 2.0 / IHE `urn:ihe:iti:adx:2015` — interopérabilité sémantique).

## 6. Ajouter un nouvel indicateur (évolution future)

1. Ajouter la clé logique dans `data_elements` du YAML (avec UID placeholder).
2. Implémenter le comptage côté `Dhis2Mapper.counts()` (uniquement du
   déterminisme : différentiels / règles matchées).
3. Ajouter un test unitaire de compte dans `tests/unit/integrations/`.
4. La clé apparaîtra automatiquement dans le validateur et l'export.
