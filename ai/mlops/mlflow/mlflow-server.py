"""Lance le serveur MLflow (SQLite backend, artifacts locaux).

Usage : python mlflow-server.py [--port 5000]
"""
import argparse

import mlflow

ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=5000)
ap.add_argument("--backend", default="sqlite:///data/mlflow.db")
ap.add_argument("--artifacts", default="data/mlartifacts")
args = ap.parse_args()

mlflow.server.run_server(
    f"{args.backend}", args.artifacts, f"0.0.0.0:{args.port}")
