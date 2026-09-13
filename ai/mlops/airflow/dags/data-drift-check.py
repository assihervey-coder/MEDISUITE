"""DAG quotidien : dérive de données (Evidently) → alerte notification-service."""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="data-drift-check",
    schedule="0 4 * * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["medisuite", "monitoring"],
) as dag:
    BashOperator(
        task_id="evidently_drift",
        bash_command=("python -m evidently calculate --config "
                      "monitoring/ml-monitoring/evidently/data-drift-config.yaml "
                      "|| curl -s -X POST http://localhost:8201/api/v1/alerte-clinique "
                      "-H 'Content-Type: application/json' -d '{\"destinataire\": "
                      "\"MLOps\", \"sujet\": \"Dérive de données détectée\"}'"),
    )
