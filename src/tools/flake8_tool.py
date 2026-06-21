from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess

class Flake8Tool(BaseTool):
    @property
    def name(self) -> str:
        return "flake8"

    @property
    def description(self) -> str:
        return "Detects PEP-8 style violations and syntax errors using Flake8."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        try:
            stdout = run_subprocess(["flake8", str(repo_path), "--exclude", "venv,.venv"])
            if not stdout:
                return []
                
            style_issues = []
            for line in stdout.splitlines():
                parts = line.rsplit(":", 3)
                if len(parts) == 4:
                    filepath = parts[0].strip()
                    error_details = parts[3].strip()
                    style_issues.append({
                        "file": filepath,
                        "issue": error_details
                    })
                    
            return style_issues
            
        except Exception:
            return []

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return

        table = Table(
            title="🎨 Style Violations (Flake8)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold blue",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Style Issue", style="dim")

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(item.get("file", ""), item.get("issue", ""))

        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        if not data:
            return "<h2>🎨 Style Violations (Flake8)</h2>\n<table>\n  <tr><th>File</th><th>Style Issue</th></tr>\n  <tr><td colspan=\"2\">No data.</td></tr>\n</table>"

        items = data if top_n is None else data[:top_n]
        rows = []
        for item in items:
            rows.append(f"<tr><td>{item.get('file', '')}</td><td>{item.get('issue', '')}</td></tr>")
        rows_str = "\n    ".join(rows)

        return f"""  <h2>🎨 Style Violations (Flake8)</h2>
  <table>
    <tr><th>File</th><th>Style Issue</th></tr>
    {rows_str}
  </table>"""
