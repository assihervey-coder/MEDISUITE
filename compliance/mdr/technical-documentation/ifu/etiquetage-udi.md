# Étiquetage et identification UDI (MDR Annexe I §23.2, Règlement UDI 2019/320)

> Statut : modèle d'étiquetage logiciel **implémenté** (v0.6.0 : écran
> « À propos » + endpoint `/api/v1/about` + `/health` version+commit) ;
> attributions 🔴 (EID GS1) — jalon R2/R8.

## 1. Étiquette logicielle (écran « À propos » + README + docs)

Chaque déploiement affiche obligatoirement (implémenté v0.6.0 : endpoint
public `GET /api/v1/about` alimentant l'écran « À propos » du web-portal,
et `/health` exposant version + commit sur les 38 services) :

```
MEDISUITE — Plateforme d'aide à la décision clinique
Version : v0.6.0 (tag Git + hash de commit)
Fabricant : ASSI Herve — Abidjan, Côte d'Ivoire
Basic UDI-DI : MEDISUITE-PLTF-AIDE-DECISION (à confirmer par émission GS1)
UDI-EID : à attribuer (agence émettrice à désigner 🔴)
Date de libération : 2026-09-14
Classe MDR : IIb (règle 11) — dispositif soumis à notification
Marquage CE : ❌ NON CE — usage clinique interdit hors cadre pilote
recherche (voir dossier technique)
```

## 2. Règles d'identification

1. **Version = tag Git sémantique** : seule référence de version reconnue ;
   toute installation doit pouvoir rendre compte de son hash de commit
   (`/health` expose `version` + `commit`).
2. **Basic UDI-DI** par famille : `MEDISUITE-PLTF-AIDE-DECISION` (plateforme
   complète) ; variantes Core/GPU tracées comme configurations (dossier CE
   §1.4), pas comme dispositifs séparés.
3. **Émission UDI** : inscription à une agence émettrice (GS1 recommandé) ;
   enregistrement EUDAMED des entités (SRN fabricant 🔴) — jalon R8.
4. **Traçabilité de lot logiciel** : le couple (tag, hash) fait foi ;
   l'image conteneur est digérée et épinglée (compose/K8s), la digération
   est consignée dans la note de déploiement.

## 3. Symboles à usage des IFU (résumé)

| Symbole/texte | Signification |
|---|---|
| « Consultez la notice d'utilisation » | IFU obligatoire avant usage |
| « Fabricant » | ASSI Herve, Abidjan |
| « Dispositif médical de classe IIb (MDR 2017/745) » | classification |
| « Non destiné à un usage pédiatrique sans protocole dédié » | limite population (hors modules pédiatrie) |
| « Ne pas utiliser en cas de doute sur l'intégrité du système » | règle d'or exploitation |
| Date de fabrication/libération (AAAA-MM-JJ) | version logicielle |

## 4. IFU — diffusion

Les 4 IFU (`IFU-clinicien.md`, `IFU-technicien.md`, `IFU-administrateur.md`,
`IFU-patient.md`) sont : publiées avec chaque release (dossier `ifu/` du
tag), accessibles depuis l'application (aide intégrée), fournies en
français (anglais en variante). Électroniques (MDR art. 23 accepte
l'IFU électronique pour dispositifs de classe IIb web — implémentation :
bouton « Notice » par écran).

## 5. Écarts déclarés (honnêteté)

- 🔴 UDI-EID non émis (dépend GS1/agence) ; SRN EUDAMED non attribué.
- 🟢 Écran « À propos » livré (v0.6.0) : `services/api-gateway/labeling.json`
  + `GET /api/v1/about` + `apps/web-portal/src/features/about/About.tsx`.
- 🔴 Notices de sécurité : gabarit à produire avec la vigilance (PROC-04).
