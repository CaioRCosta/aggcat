"""Módulo de análise estática"""

from __future__ import annotations
from pathlib import Path
import json
import subprocess

from aggcat import config

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
    
def run_bandit(repo_path: Path) -> list[dict]:
    """Executa o Bandit para encontrar falhas de segurança"""
    try:
        # A flag -x exclui diretórios e -f json formata a saída
        # O Bandit retorna código de erro se achar vulnerabilidades,
        # por isso check=False
        result = subprocess.run(
            ["bandit", "-r", str(repo_path), "-x", "venv,.venv", "-f", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if not result.stdout.strip():
            return []
            
        data = json.loads(result.stdout)
        security_issues = []
        
        for issue in data.get("results", []):
            severity = issue.get("issue_severity", config.SEVERITY_LOW)
            security_issues.append({
                "file": issue.get("filename", ""),
                "severity": severity,
                "issue": issue.get("issue_text", "")
            })
            
        # Ordena colocando os de alta severidade no topo da lista
        severity_order = {
            config.SEVERITY_HIGH: 0, 
            config.SEVERITY_MEDIUM: 1, 
            config.SEVERITY_LOW: 2
        }
        security_issues.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        return security_issues
        
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def run_vulture(repo_path: Path) -> list[dict]:
    """Executa o Vulture para encontrar código morto"""
    try:
        # O Vulture não tem saída nativa em JSON, então faz o parsing do texto puro
        result = subprocess.run(
            [
                "vulture", 
                str(repo_path), 
                "--min-confidence", 
                str(config.VULTURE_MIN_CONFIDENCE),
                "--exclude", "venv,.venv"
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        if not result.stdout.strip():
            return []
            
        dead_code = []
        # A saída padrão é no formato: "caminho_arquivo.py:linha: mensagem (confiança)"
        for line in result.stdout.splitlines():
            if ":" in line:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    dead_code.append({
                        "file": parts[0].strip(),
                        "issue": parts[2].strip()
                    })
                    
        return dead_code
        
    except FileNotFoundError:
        return []
    
def run_flake8(repo_path: Path) -> list[dict]:
    """Executa o Flake8 para encontrar violações de estilo (PEP-8) e erros de sintaxe"""
    try:
        # Executa o flake8 ignorando os ambientes virtuais
        result = subprocess.run(
            ["flake8", str(repo_path), "--exclude", "venv,.venv"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if not result.stdout.strip():
            return []
            
        style_issues = []
        # Saída padrão do Flake8: "caminho_arquivo.py:linha:coluna: CODIGO Mensagem"
        for line in result.stdout.splitlines():
            # Divide a string em no máximo 4 partes: arquivo, linha, coluna, erro
            parts = line.split(":", 3)
            if len(parts) == 4:
                filepath = parts[0].strip()
                error_details = parts[3].strip()
                style_issues.append({
                    "file": filepath,
                    "issue": error_details
                })
                
        return style_issues
        
    except FileNotFoundError:
        return []
    
def run_lizard(repo_path: Path) -> list[dict]:
    """Executa o Lizard para calcular a complexidade ciclomática"""
    try:
        # -C define o limite de complexidade
        # -w faz imprimir apenas os warnings (funções muito complexas)
        result = subprocess.run(
            [
                "lizard", 
                str(repo_path), 
                "-C", str(config.CC_LOW), 
                "-w", 
                "-x", "*/venv/*", 
                "-x", "*/.venv/*"
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        if not result.stdout.strip():
            return []
            
        complex_files = []
        # Saída de warning do Lizard: "caminho_arquivo.py:linha: warning: func tem X CCN"
        for line in result.stdout.splitlines():
            if " warning: " in line.lower():
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    filepath = parts[0].strip()
                    issue_msg = parts[2].strip()
                    complex_files.append({
                        "file": filepath,
                        "issue": issue_msg
                    })
                    
        return complex_files
        
    except FileNotFoundError:
        return []

def run(repo_path: str | Path) -> dict:
    path = Path(repo_path).resolve()
    
    return {
        "maintainability": run_radon(path),
        "security": run_bandit(path),
        "dead_code": run_vulture(path),
        "style": run_flake8(path),
        "complexity": run_lizard(path),
    }