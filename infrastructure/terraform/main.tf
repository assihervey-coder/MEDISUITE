# MEDISUITE — infra as code (ADR-0011)
# modules/ : kubernetes, database, storage, networking, monitoring, security, gpu-nodes, backup
module "namespace" {
  source   = "./modules/kubernetes"
  name     = var.environment
  labels   = {app.kubernetes.io/part-of = "medisuite"}
}

variable "environment" {
  description = "dev | staging | production"
  type        = string
  default     = "dev"
}
