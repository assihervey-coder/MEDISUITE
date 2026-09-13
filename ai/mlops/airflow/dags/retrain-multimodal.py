"""DAG de ré-entraînement de la fusion multimodale (hebdomadaire).

Déclenche prepare → train → evaluate → (promotion si seuil atteint).
Référence : docs/ml/model-lifecycle.md
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator

default_args = {"retries": 2, "retry_delay": timedelta(minutes=10)}

with DAG(
    dag_id="retrain-multimodal",
    schedule="0 2 * * 1",  # lundi 2h UTC
    start_date=datetime(2026, 9, 1),
    catchup=False,
    default_args=default_args,
    tags=["medisuite", "mlops", "multimodal"],
) as dag:
    drift = BashOperator(
        task_id="check_data_drift",
        bash_command="python scripts/ml/check-drift.py --fail-above 0.2 || exit 1",
    )
    train = BashOperator(
        task_id="train",
        bash_command="dvc repro train_fusion evaluate",
    )
    gate = BranchPythonOperator(
        task_id="quality_gate",
        python_callable=lambda: "promote" if _auc_above(0.85) else "hold",
    )
    promote = BashOperator(
        task_id="promote",
        bash_command="python scripts/ml/register-model.py --stage production",
    )
    hold = BashOperator(task_id="hold",
                        bash_command="echo 'qualité insuffisante — pas de promotion'")

    drift >> train >> gate >> [promote, hold]


def _auc_above(threshold: float) -> bool:
    """Lit eval.json et compare à la borne de qualité clinique."""
    import json
    from pathlib import Path
    p = Path("ai/models/fusion/eval.json")
    return p.exists() and json.loads(p.read_text()).get("auc", 0) >= threshold
