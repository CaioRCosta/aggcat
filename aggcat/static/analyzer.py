"""Módulo de análise estática"""

from __future__ import annotations
from pathlib import Path
import json
import subprocess

def run_radon(repo_path: Path) -> list[dict]:
    """Executa o Radon para calcular o índice de manutenibilidade (MI)"""
    try:
        result = subprocess.run(
            ["radon", "mi", "-j", "-i", "venv,.venv", str(repo_path)],
            capture_output=True,
            text=True,
            check=False
        )
        if not result.stdout.strip():
            return []
            
        data = json.loads(result.stdout)
        maintainability = []
        
        for filepath, details in data.items():
            mi_score = details.get("mi", 0.0)
            maintainability.append({
                "file": filepath,
                "mi": round(mi_score, 2)
            })
            
        maintainability.sort(key=lambda x: x["mi"])
        return maintainability
        
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def run(repo_path: str | Path) -> dict:
    path = Path(repo_path).resolve()
    
    return {
        "maintainability": run_radon(path),
        "security": [],
    }