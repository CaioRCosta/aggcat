"""Módulo de análise estática"""

from __future__ import annotations
from pathlib import Path

def run(repo_path: str | Path) -> dict:
    path = Path(repo_path).resolve()
    
    return {
        "maintainability": [],
        "security": [],
    }