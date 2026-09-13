# Analyse d'écarts réglementaire — MEDISUITE v0.1.0

> Honnêteté d'ingénieur : ce tableau distingue ce qui est **implémenté**, ce qui est
> **documenté mais à exécuter**, et ce qui **manque** avant toute utilisation clinique.

| Exigence | Statut v0.1 | Écart / action |
|---|---|---|
| MDR 2017/745 — classification | ⚠️ postulat IIb (ADR-0004) | Trancher règle par règle (Rule 11) avec un organisme notifié |
| ISO 13485 (SMQ) | 🔴 non implanté | Qualité manuelle à créer avant validation clinique |
| IEC 62304 (logiciel, niveau C) | 🟠 partiel — architecture testée (226+ tests), lifecycle non audité | Écrire le plan logiciel + dossier V&V |
| ISO 14971 (gestion des risques) | 🟠 risques R1-R10 identifiés (audit) | FMEA complet + évaluation a posteriori |
| IEC 81001-5-1 (traçabilité) | ✅ registre audit chaîné + vérification | Extension aux flux HL7/DICOM |
| RGPD art. 7 (consentements) | ✅ consentements révocables par patient | DPIA complets (5 modules) à finaliser |
| RGPD art. 32 (sécurité) | 🟠 scrypt, JWT, pseudonymisation, .gitignore durci | Vault + TLS mTLS + tests d'intrusion |
| HDS (hébergement) | 🔴 n/a hors UE | Hébergeur certifié requis pour la CI si données transfrontalières |
| Explicabilité IA | ✅ importance des modalités, attention | SHAP/GradCAM natifs (v0.2) |
| Dérive de modèles | 🟠 DAG Airflow data-drift-check | Seuils à calibrer sur données réelles |

**Conclusion** : le socle technique est conforme « by design » ; la conformité
juridique est un processus (certification = le produit, audit 2026). Aucune mise
en production clinique sans marquage CE.
