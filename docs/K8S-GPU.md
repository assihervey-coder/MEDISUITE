# Déploiement Kubernetes GPU (v0.4)

Manifests d'inférence IA sur GPU pour le moteur de fusion multimodale et les
têtes de prédiction. L'objectif opérationnel : **2 pods d'inférence toujours
disponibles** ( RollingUpdate sans indisponibilité), sur des GPU partagés par
**time-slicing** pour tenir le coût d'exploitation d'un CHU ivoirien.

## 1. Contenu de l'overlay

```
infrastructure/kubernetes/gpu/
├── runtimeclass.yaml        # RuntimeClass nvidia (handler nvidia)
├── device-plugin.yaml       # DaemonSet nvidia-device-plugin v0.16.2
│                            # + ConfigMap time-slicing (2 replicas/GPU)
├── fusion-inference.yaml    # PriorityClass + Deployment multimodal-gateway
│                            # + Service :8022 + HPA (cpu 70 %, 2→6 pods)
└── kustomization.yaml       # kubectl apply -k infrastructure/kubernetes/gpu/
```

## 2. Prérequis nœuds

1. Pilotes NVIDIA installés + `nvidia-container-toolkit` (ou **GPU Operator**).
2. Nœuds labellisés `nvidia.com/gpu.present: "true"` (le device plugin pose
   ce label automatiquement une fois les drivers détectés).
3. Taint recommandé : `kubectl taint nodes <gpu-node> nvidia.com/gpu=:NoSchedule`
   — les pods MEDISUITE GPU portent déjà la tolération correspondante.

## 3. Déploiement

```bash
kubectl apply -k infrastructure/kubernetes/gpu/
# vérification
kubectl get pods -n medisuite -l app=multimodal-gateway
kubectl describe node <gpu-node> | grep -A3 "nvidia.com"   # slices alloués
```

Le pod d'inférence demande explicitement `nvidia.com/gpu: 1` (limites ET
requêtes) : le scheduler ne le place que sur un nœud disposant d'une slice
libre, via la RuntimeClass `nvidia` (`runtimeClassName` dans le pod spec).

## 4. Choix d'ingénierie (et compromis assumés)

| Décision | Justification | Compromis |
|---|---|---|
| **Time-slicing ×2** | coût GPU ÷2, suffisant pour des inférences d'encodage (ms) | isolation mémoire nulle : un pod saturant le GPU impacte son voisin — acceptable en inférence courte, prohibé en entraînement |
| **HPA sur CPU (70 %)** | métrique standard sans dépendance DCGM | indirect : c'est la saturation GPU qui fait monter le CPU d'orchestration — HPA DCGM `nvidia.com/gpu.utilization` à brancher en v1.0 via Prometheus Adapter |
| **`runAsNonRoot: true`, capabilities ALL drop** | durcissement MDR/ISO 14971 (maîtrise des erreurs d'intégration) | images à construire avec USER 1000 (Dockerfile v0.4) |
| **RollingUpdate maxUnavailable: 0** | aucune coupure de service d'inférence | maxSurge: 1 exige temporairement une 3e slice GPU |
| **PriorityClass 100 000** | l'inférence clinique préempte les batchs MLOps | les jobs d'entraînement (Kubeflow) doivent rester en priority basse |

## 5. Observabilité

Les pods GPU héritent du middleware OTel (`MEDISUITE_OTEL_ENDPOINT` pointant
vers le collecteur en namespace `observability`) : chaque requête d'inférence
est traçée (`http.duration_ms`) — base de la détection de régression de
latence lors des mises à jour de modèles (cf. plan PMS v1.0, dossier CE).

## 6. Limites connues

- **Pas de NetworkPolicy dans l'overlay GPU** : à poser avec l'ingress
  production (v1.0) — le principe est déjà appliqué au référentiel HAPI.
- **Image non publiée** : `ghcr.io/assihervey-coder/medisuite/multimodal-gateway:0.4.0`
  est la cible ; la CI GitHub Actions la construira dès l'activation des
  runners (les tests unitaires torch/monai du dépôt couvrent la logique).
- **Time-slicing ≠ MIG** : pour des modèles lourds (segmentation 3D), préférer
  MIG (A100/H100) en v1.0 ; le ConfigMap est le seul fichier à changer.
- **Pas de quota GPU par namespace** : ResourceQuota `requests.nvidia.com/gpu`
  à ajouter quand plusieurs équipes partageront le cluster.
