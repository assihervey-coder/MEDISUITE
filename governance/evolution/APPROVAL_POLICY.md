# APPROVAL_POLICY

Source machine : `evolution-control-plane/config/approval-matrix.yaml`.

- P1/P2 : pas d'approbation humaine (CI suffit).
- P3 : 1 approbateur (maintainer).
- P4 : maintainer + security_officer.
- P5 : maintainer + data_protection (DPO).
- P6 : maintainer + clinical_lead.
- P7 : clinical_lead + safety_officer.
- P8 : clinical_lead + safety_officer + security_officer.
- P9 : regulatory_affairs + clinical_lead + safety_officer.

Règles transverses : pas d'auto-approbation ; quorum = liste complète pour « committee » ;
chaque approbation horodate + motif + evidence_id ; refus motivé obligatoire.
