# Datasets synthétiques des 26 modules (v0.6.0)

> ⚠️ **AUCUNE donnée réelle.** Tout est généré de façon déterministe
> (`seed 42`) par `generate.py` + `registry.py`. Interdits pour
> l'entraînement d'un modèle clinique validé — réservés aux smoke trains,
> tests d'intégration de la fusion, démonstrations de drift et maquettes.
> Les données d'entraînement réelles viendront de l'investigation
> multicentrique (protocole R5, dossier CE §10).

## Contenu

```
datasets/
├── registry.py      # registre : features cliniques nommées + schémas de labels
├── generate.py      # générateur déterministe (flux RNG par module)
├── manifest.json    # schémas, comptages, SHA-256 par module, seed, note légale
├── tests/           # 6 tests : manifest, schéma, déterminisme, signal, ADR-0018
└── <slug>/          # 26 répertoires (imaging … emergency)
    ├── train.jsonl  # 120 lignes
    └── val.jsonl    # 30 lignes
```

## Format d'une ligne (JSONL)

```json
{
  "id": "m13-t00042", "module": 13, "slug": "neurology",
  "split": "train", "task": "classification", "synthetique": true,
  "patient": {"id": "pat…", "sexe": "M", "age": 68},
  "modalites": {
    "imaging_3d": [-0.95, 0.12, …],          // vecteur 16-D (encoder image 3D)
    "tabulaire": {"nihss": 12.4, "aspects": 6.1, …},  // features cliniques
    "texte": "neurology: nihss=12.40, aspects=6.10. Synthétique."
  },
  "manquantes": ["texte"],                   // ADR-0018 : ≤1, jamais la primaire
  "label": 1                                 // schéma selon la tâche du module
}
```

Schémas de label par tâche : `classification` → 0/1 ; `multiclass` → entier
indexant `classes` ; `multilabel` → tuple binaire ; `regression` /
`segmentation` → flottant borné [`lo`, `hi`]. Les tâches sont reprises des
configs IA (`ai/multimodal/configs/*.yaml`) — `binary` y est normalisé en
`classification`.

## Propriétés garanties (testées)

| Propriété | Garantie | Test |
|---|---|---|
| Couverture | 26/26 modules, SHA-256 consignés | `test_manifest_couple_les_26_modules` |
| Intégrité | SHA-256 du manifest = fichiers | `test_manifest_sha256_cohérents_avec_fichiers` |
| Schéma | chaque ligne conforme à sa tâche | `test_schema_lignes_par_tache` |
| Déterminisme | même seed → mêmes octets (même en `--only`) | `test_determinisme_regeneration_cardiology` |
| Signal apprenant | discriminantes ∝ label | `test_signal_apprenant_neurology` |
| Modalités manquantes | ≤ 1, jamais la primaire (ADR-0018) | `test_modalites_manquantes_politique` |

## Génération

```bash
python datasets/generate.py                       # 26 modules, seed 42
python datasets/generate.py --only cardiology     # un module (identique)
python datasets/generate.py --train 500 --val 100 # volumes supérieurs
pytest datasets/tests/ -q                         # validation
```

Le flux RNG est **par module** (`seed*100 + no`) : régénérer ou ajouter un
module ne modifie jamais les octets des autres modules — le manifest garde
donc une valeur de lignée stable pour DVC (`ai/mlops/dvc/`).

## Usage avec la fusion (exemples)

```python
import json, sys
sys.path.insert(0, "ai")
from multimodal.factory import fusion_model_for_module

rows = [json.loads(l) for l in open("datasets/cardiology/train.jsonl")]
model = fusion_model_for_module(8)   # config 08_cardiology.yaml (torch si installé)
# l'inférence attend les modalités présentes par row :
# model.infer({"signal_1d": r["modalites"]["signal_1d"], "tabulaire": r["modalites"]["tabulaire"], …})
```

Le tableau croisé modules ↔ configs ↔ datasets ↔ services est consigné dans
`docs/audit-26-modules.md` (audit v0.6.0).
