# UDI-EID GS1 — identifiants du dispositif MEDISUITE (v0.7.0)

> Périmètre : tout ce qui est **codifiable** de la chaîne UDI est
> implémenté dans `medisuite_core/gs1_udi.py` (17 tests) et exposé dans
> `labeling.json` / écran « À propos ». Ce qui est **physique** reste
> 🔴 terrain (jalon R8) : adhésion GS1 Côte d'Ivoire, attribution du
> préfixe entreprise réel, impression des DataMatrix sur site.

## Structure implémentée

| Objet | Implémentation | Statut |
|---|---|---|
| GTIN-13/14 + clé mod-10 (AI 01) | `build_gtin14`, `validate_gtin` | 🟢 |
| Basic UDI-DI (GTIN-14 indicateur « 0 ») | `basic_udi_di()` | 🟢 code / 🔴 émission GS1 |
| Dates YYMMDD (AI 11/17, jour 00 = fin de mois) | `fmt_gs1_date`, `parse_gs1_date` | 🟢 |
| Lot (AI 10) / série (AI 21), jeu de caractères fail-closed | `_check_var` | 🟢 |
| Élément-string DataMatrix (FNC1 0x1D, ordre 01/17/11/10/21) | `build_element_string`, `parse_element_string` | 🟢 |
| GS1 Digital Link → EID (résolveur `id.gs1.org`) | `gs1_digital_link` | 🟢 code / 🔴 résolveur fabricant |
| Étiquette complète (MDR Annexe I §23.2) | `label_payload`, `verify_label_payload` | 🟢 |
| Adhésion GS1 CI + préfixe définitif + impression | — | 🔴 R8 (terrain) |

## Exemple (préfixe de DÉMONSTRATION — ne pas produire)

```
Base 12 chiffres (préfixe 260 + référence modèle) : 260000000001
Basic UDI-DI (GTIN-14, indicateur 0)             : 02600000000017
GTIN unité installée                             : 03760221760012
Élément-string (DataMatrix) :
  0103760221760012172712311126091410LOT42\x1d21SN001
  → (01)03760221760012 (17)271231 (11)260914 (10)LOT42 (21)SN001
GS1 Digital Link :
  https://id.gs1.org/01/03760221760012/10/LOT42/21/SN001
```

Le parseur rejette (fail-closed) : clé de contrôle invalide, AI inconnu,
caractères hors jeu des AIs variables (l'espace n'appartient pas au jeu
GS1), dates inexistantes, absence du (01) en tête.

## Intégration au reste de la plateforme

- `services/api-gateway/labeling.json` : bloc `gs1` (émetteur, AIs,
  statut honnête « proposé — adhésion 🔴 ») + version v0.7.0 ; servi
  publiquement par `GET /api/v1/about` (écran « À propos » du portal).
- Étiquetage logique versionné = tag Git (`ifu/etiquetage-udi.md`) ;
  le couple (version, commit) reste la règle 1 de l'étiquette.
- `docs/UDI-GS1.md` (ce document) est référencé par le dossier technique
  (`01-identification-classification.md`).

## Chemin vers l'attribution réelle (R8, terrain)

1. Adhésion GS1 Côte d'Ivoire → préfixe entreprise définitif (remplace
   `260` de démonstration).
2. Attribution des GTINs (modèle + niveaux d'emballage) et du Basic
   UDI-DI ; mise à jour de `labeling.json` (fini le statut « proposé »).
3. Enregistrement des UDI-DI dans EUDAMED à la mise sur marché (après CE).
4. Impression/gravure des DataMatrix (postes sites) + vérification de
   grade d'impression ISO/IEC 15415 — hors périmètre logiciel.
