# MEDISUITE — visualiseur OHIF v3 branché sur /dicom-web (v0.3)
#
# Image officielle OHIF (nginx + SPA) surchargée par :
#  - app-config.js : source de données DICOMweb « orthanc » (chemins relatifs)
#  - nginx.conf     : proxy /dicom-web + /wado → orthanc-pacs:8042 avec
#                     authentification injectée côté serveur
# Build : docker compose -f local-deployment/docker-compose.minimal.yml build ohif
FROM ohif/app:v3.8.3

COPY app-config.js /usr/share/nginx/html/app-config.js
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
# nginx de l'image officielle démarre en ENTRYPOINT — rien à redéfinir
