# Politique de refus

TropiRAG refuse poliment mais fermement quand :
- la preuve est insuffisante (insufficient_evidence) ;
- la demande sort du périmètre fièvre+voyage (outside_scope) ;
- l'utilisateur exige un diagnostic autonome (autonomous_diagnosis_forbidden) ;
- la sortie IA échoue aux gardes (hallucination_detected) ;
- une injection de prompt est détectée (injection_detected).

Format de refus : motif + ce qui est nécessaire pour avancer (données,
examens, clinicien senior). Le refus est TOUJOURS constructif.
