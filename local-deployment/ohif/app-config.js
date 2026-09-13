/**
 * MEDISUITE — configuration OHIF v3 (viewer médical) pour le PACS Orthanc local.
 *
 * Source de vérité : https://docs.ohif.org/configuration/data-sources/dicomweb
 * Tous les appels DICOMweb (QIDO-RS / WADO-RS) partent en chemins RELATIFS
 * (/dicom-web) et sont résolus par le nginx embarqué du conteneur OHIF
 * (voir nginx.conf) qui proxifie vers orthanc-pacs:8042 en injectant les
 * identifiants PACS côté serveur — le navigateur ne voit JAMAIS le secret.
 *
 * Lien profond d'une étude : http://localhost:3001/viewer?StudyInstanceUIDs=<uid>
 * (généré par imaging-service : GET /api/v1/pacs/viewer-url?study_uid=…)
 */
window.config = {
  routerBasename: '/',
  showStudyList: true,
  defaultDataSourceName: 'orthanc',
  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'orthanc',
      configuration: {
        friendlyName: 'MEDISUITE PACS — Orthanc (DICOMweb PS3.18)',
        name: 'MEDISUITE-PACS',
        // Racines DICOMweb — identiques au bloc DicomWeb de orthanc.json
        wadoUriRoot: '/wado',      // WADO-URI (PS3.18 annexe C, images brutes)
        qidoRoot: '/dicom-web',    // QIDO-RS : recherche d'études/séries/instances
        wadoRoot: '/dicom-web',    // WADO-RS : récupération métadonnées + pixels
        qidoSupportsIncludeField: true,
        imageRendering: 'wadors',
        thumbnailRendering: 'wadors',
        enableStudyLazyLoad: true,
        supportsFuzzyMatching: true,
        supportsWildcard: true,
        supportsReject: false,
        staticWado: false,
        singlepart: 'bulkdata,video',
        bulkDataURI: { enabled: true },
        // Transfert pixels : JPEG Lossless (universellement supporté par Orthanc)
        requestTransferSyntaxUID: '1.2.840.10008.1.2.4.70',
      },
    },
  ],
};
