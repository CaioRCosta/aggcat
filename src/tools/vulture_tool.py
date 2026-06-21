from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess

class VultureTool(BaseTool):
    VULTURE_MIN_CONFIDENCE = 80

    @property
    def name(self) -> str:
        return "vulture"
    
    @property
    def description(self) -> str:
        return "Detects unused code (functions, classes, variables) using Vulture."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        try:
            stdout = run_subprocess([
                "vulture", 
                str(repo_path), 
                "--min-confidence", 
                str(self.VULTURE_MIN_CONFIDENCE),
                "--exclude", "venv,.venv"
            ])
            if not stdout:
                return []
                
            dead_code = []
            for line in stdout.splitlines():
                if ":" in line:
                    parts = line.rsplit(":", 2)
                    if len(parts) >= 3:
                        dead_code.append({
                            "file": parts[0].strip(),
                            "issue": parts[2].strip()
                        })
                        
            return dead_code
            
        except Exception:
            return []

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return

        table = Table(
            title="💀 Unused Code (Vulture)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold red",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Unused Code / Issue", style="dim")

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(item.get("file", ""), item.get("issue", ""))

        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        if not data:
            return "<h2>💀 Unused Code (Vulture)</h2>\n<table>\n  <tr><th>File</th><th>Unused Code / Issue</th></tr>\n  <tr><td colspan=\"2\">No data.</td></tr>\n</table>"

        items = data if top_n is None else data[:top_n]
        rows = []
        for item in items:
            rows.append(f"<tr><td>{item.get('file', '')}</td><td>{item.get('issue', '')}</td></tr>")
        rows_str = "\n    ".join(rows)

        return f"""  <h2>💀 Unused Code (Vulture)</h2>
  <table>
    <tr><th>File</th><th>Unused Code / Issue</th></tr>
    {rows_str}
  </table>"""
