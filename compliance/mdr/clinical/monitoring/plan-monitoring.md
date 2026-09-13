# Plan de monitoring — Investigation MEDISUITE-CI-01

> **Étude** MEDISUITE-CI-01 · **Protocole** v1.0-draft (TD-10, annexe A4) ·
> **Base** ISO 14155:2020 §5.6 (monitoring) + protocole §7.5 · **Statut** :
> 🟢 outil rédigé — exécution par moniteur indépendant contractuel 🔴 terrain
> (jalon R6, fenêtre M+6 → M+18).

## 1. Objectif du monitoring

Vérifier : (a) les droits et le bien-être des participants sont protégés ;
(b) les données eCRF sont exactes, complètes et vérifiables vis-à-vis des
sources (SDV) ; (c) le protocole, l'EGSP et les exigences réglementaires
(ANOC-CI, Ministère, MDR Annexe XV art. 62-80) sont respectés. Le monitoring
ne remplace ni l'audit (PROC-08) ni l'inspection : il est continu, planifié,
et tracé. La séparation est stricte : le moniteur **n'intervient jamais** sur
la saisie (`ecrf.write` interdit à son rôle) — il ouvre des requêtes que le
site clôt, et ses exports passent par l'export DSMB agrégé sans PHI.

## 2. Stratégie par site et par phase

| Phase | Visites | Période | Fréquence | SDV |
|---|---|---|---|---|
| Initiation | 1 par site (V0) | avant 1ʳᵉ inclusion (M+6) | — | — |
| Intermédiaire | V1-V6 par site | M+6 → M+16 | toutes 6 semaines ± 2 sem. | 20 % des entrées, 100 % des SAE, 100 % des consentements |
| Clôture | 1 par site (VC) | avant lock M+18 | — | 100 % des requêtes résolues vérifiées |

Critères d'intensification (déclenchent une visite ad hoc sous 2 semaines) :
taux de requêtes SDV > 15 % sur un site ; déviation majeure ; inclusion
anormalement rapide (recrutement suspect) ; écart de délai P3 médian > 25 %
vs médiane étude (signal de biais de saisie).

## 3. Vérifications systématiques à chaque visite

1. **Consentements** : original présent, signé daté avant tout acte
   d'inclusion, version d'information en vigueur ; consentement différé
   d'urgence (§5.2) ré-information tracée dans les 24 h.
2. **Éligibilité** : F01 cohérent avec la source (âge, grossesse, perte de
   modalités ≤ 1 ADR-0018, absence de doublon 14 j, panne site 24 h).
3. **Sécurité** : tous les EI/SAE (F04) reportés dans les délais
   (24 h promoteur/DSMB ; ≤ 7 j ANOC-CI + Ministère ; vigilance MDR art. 87-90
   si incident grave impliquant le DM) ; cohérence entre F04 saisis et
   registre EI du site.
4. **Délais** (endpoint P3) : horodatages sources (arrivée, imagerie,
   décision) concordants avec F03 ; dérivations `derive_delai_minutes`
   vérifiées par recalcul.
5. **Adjudication** : statut des cas flous transmis au comité (F05) ; le site
   ne connaît pas le verdict avant clôture du sujet (aveuglement §3.3).
6. **Traçabilité système** : `/api/v1/ecrf/audit/verify` exécuté en séance —
   la chaîne SHA-256 doit être `integre: true` ; toute rupture = déviation
   majeure immédiate + notification promoteur sous 24 h.
7. **Matériel** : Basic UDI-DI de la plateforme en service au site, version
   logicielle déployée (= version d'investigation figée du protocole),
   journal des pannes site (`panne_site_24h`).
8. **Requêtes SDV** : état des requêtes ouvertes via `/api/v1/ecrf/queries`,
   négociation des délais de réponse (≤ 10 jours ouvrés).

## 4. Rapports et délais

- **Rapport de visite** (modèle `modele-rapport-visite-A4.md`, format A4) :
  signé du moniteur, envoyé au promoteur et au coordonnateur du site sous
  **5 jours ouvrés** après la visite ; le site répond aux actions sous
  **10 jours ouvrés**.
- **Lettre de suivi** : relance systématique à J+11 si actions ouvertes ;
  escalade au promoteur (J+21) puis au DSMB si sécurité en jeu.
- **Registre des déviations** (`registre-deviations.md`) : tenu central,
  revu à chaque réunion DSMB ; toute déviation majeure → évaluation
  bénéfice-risque mise à jour (ISO 14971, RM-01…RM-10) si elle révèle un
  nouveau risque.
- **Enregistrements** : rapports signés, lettres, registre — conservés
  25 ans (dossier d'investigation, MDR 2017/745 annexe XV).

## 5. Préparation du lock (M+18)

La dernière visite (VC) précède le verrouillage de la base : le moniteur
atteste (i) zéro requête ouverte, (ii) SDV finale 100 % SAE, (iii) signatures
investigateur complètes. Le promoteur exécute alors
`POST /api/v1/ecrf/study/lock` (≥ 2 témoins), qui fige un checksum SHA-256 de
l'ensemble des entrées — **prérequis bloquant** de l'extraction d'analyse du
data manager (`GET /api/v1/ecrf/extract`), qui refuse toute extraction avant
le lock. Détail opérationnel : docs/E-CRF.md §verrou.
