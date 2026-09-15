"""Gouvernance clinique de TropiRAG — verrou d'investigation M+18.

Toutes les sorties du module CDS (cases, evidence, synthèse IA) sont des
sorties d'INVESTIGATION : le protocole MEDISUITE-CI-01 (MDR Annexe XV /
ISO 14155) interdit toute décision clinique fondée sur ces sorties tant
que le verrou de base M+18 n'a pas été suivi du rapport clinique (R7)
puis du marquage CE (R8).

Ce paquet matérialise l'interdiction (défense en profondeur) :
    - investigation.py  : descripteur versionné + calendrier M+/ISO 8601 ;
    - middleware/api    : tampon `governance` sur les réponses décisionnelles
      (corps JSON + en-têtes X-Governance-*) ;
    - routes API        : GET /api/v1/governance (état public du verrou) et
      POST /api/v1/decision/finalize → 451 Unavailable For Legal Reasons
      tant que le verrou est actif (fail-closed, journalisé).
"""
