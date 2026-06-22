import json
from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess

class BanditTool(BaseTool):
    SEVERITY_HIGH = "HIGH"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_LOW = "LOW"

    @property
    def name(self) -> str:
        return "bandit"
    
    @property
    def description(self) -> str:
        return "Detects security vulnerabilities in Python code using Bandit."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        try:
            exclude = ",".join(
                str(p) for name in ("venv", ".venv", "__pycache__", ".git")
                if (p := (Path(repo_path) / name)).exists()
            )
            cmd = ["bandit", "-r", str(repo_path), "-f", "json"]
            if exclude:
                cmd += ["-x", exclude]
            stdout = run_subprocess(cmd)
            if not stdout:
                return []
                
            data = json.loads(stdout)
            security_issues = []
            
            for issue in data.get("results", []):
                severity = issue.get("issue_severity", self.SEVERITY_LOW)
                security_issues.append({
                    "file": issue.get("filename", ""),
                    "severity": severity,
                    "issue": issue.get("issue_text", "")
                })
                
            severity_order = {
                self.SEVERITY_HIGH: 0, 
                self.SEVERITY_MEDIUM: 1, 
                self.SEVERITY_LOW: 2
            }
            security_issues.sort(key=lambda x: severity_order.get(x["severity"], 3))
            
            return security_issues
            
        except Exception:
            return []

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return

        table = Table(
            title="🔐 Security Issues",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold magenta",
        )
        table.add_column("File / Package", style="cyan", no_wrap=True)
        table.add_column("Severity", justify="center")
        table.add_column("Issue", style="dim")

        items = data if top_n is None else data[:top_n]
        for item in items:
            severity = item.get("severity", "LOW")
            color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(severity, "white")
            table.add_row(
                item.get("file", ""),
                Text(severity, style=color),
                item.get("issue", ""),
            )

        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        if not data:
            return "<h2>🔐 Security Issues</h2>\n<table>\n  <tr><th>File / Package</th><th>Severity</th><th>Issue</th></tr>\n  <tr><td colspan=\"3\">No data.</td></tr>\n</table>"

        items = data if top_n is None else data[:top_n]
        rows = []
        for item in items:
            rows.append(f"<tr><td>{item.get('file', '')}</td><td>{item.get('severity', '')}</td><td>{item.get('issue', '')}</td></tr>")
        rows_str = "\n    ".join(rows)

        return f"""  <h2>🔐 Security Issues</h2>
  <table>
    <tr><th>File / Package</th><th>Severity</th><th>Issue</th></tr>
    {rows_str}
  </table>"""
