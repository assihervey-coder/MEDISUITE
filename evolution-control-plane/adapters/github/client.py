"""Adaptateur GitHub — V1 : lecture API REST (runs, jobs) sans dépendance.

Le token n'est JAMAIS loggé ; il vient de l'environnement (GITHUB_TOKEN).
"""
from __future__ import annotations

import os
import urllib.request
import json

API = "https://api.github.com"


class GitHubClient:
    def __init__(self, repo: str = "assihervey-coder/MEDISUITE",
                 token: str | None = None) -> None:
        self.repo = repo
        self.token = token or os.environ.get("GITHUB_TOKEN", "")

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(
            f"{API}/repos/{self.repo}/{path}",
            headers={"Authorization": f"Bearer {self.token}",
                     "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def latest_run(self) -> dict:
        runs = self._get("actions/runs?per_page=1")
        return (runs.get("workflow_runs") or [{}])[0]
