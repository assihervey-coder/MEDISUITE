"""Moteur de règles cliniques MEDISUITE — la source unique de vérité clinique.

Principes :
1. Chaque score est une **fonction pure** : entrées numériques/booléennes → dict résultat.
2. Chaque docstring **cite le référentiel** (guideline + année + section si pertinente).
3. Chaque score a des tests unitaires sur cas limites (packages/clinical-rules/tests).
4. Les services importent ces fonctions — jamais de logique clinique copiée-collée.

Modules par domaine : triage, emergency, cardiology, pneumology, nephrology,
oncology, gyne_obstetrique, neurology, psy_geriatrie, derma_ent_ophtalmo,
gastro_rheuma_uro, lab_qc, scores.
"""
__version__ = "0.1.0"
