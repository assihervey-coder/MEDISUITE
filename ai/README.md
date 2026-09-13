# ai/ — Intelligence artificielle MEDISUITE

- `multimodal/` : moteur de fusion cross-attention résilient aux modalités
  manquantes (implémentation de référence NumPy, poids entraînés en v0.2 — ADR-0016/17/18)
- `mlops/` : MLflow (tracking/registry), DVC (données versionnées), Feast (features),
  Airflow (ré-entraînement + dérive), Kubeflow/KServe (pipelines + serving GPU)
- `privacy/` : apprentissage fédéré, DP-SGD, données synthétiques (v0.2 — ADR-0014)
- `evaluation/` : métriques cliniques, validation externe multicentrique (v0.2)

Test rapide : `cd ai && python -m pytest multimodal/tests/ -q`
