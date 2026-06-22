from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess

class LizardTool(BaseTool):
    @property
    def name(self) -> str:
        return "lizard"
    
    @property
    def description(self) -> str:
        return "Executes Lizard to calculate cyclomatic complexity warnings."

    @property
    def defaults(self) -> Dict[str, Any]:
        return {
            "cc_low": 10,
        }

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        cc_low = self._get_config("cc_low")
        try:
            stdout = run_subprocess([
                "lizard", 
                str(repo_path), 
                "-C", str(cc_low), 
                "-w", 
                "-x", "*/venv/*", 
                "-x", "*/.venv/*"
            ])
            if not stdout:
                return []
                
            complex_files = []
            for line in stdout.splitlines():
                if " warning: " in line.lower():
                    parts = line.rsplit(":", 2)
                    if len(parts) >= 3:
                        filepath = parts[0].strip()
                        issue_msg = parts[2].strip()
                        complex_files.append({
                            "file": filepath,
                            "issue": issue_msg
                        })
                        
            return complex_files
            
        except Exception:
            return []

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return

        table = Table(
            title="⚡ Cyclomatic Complexity Warnings (Lizard)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold yellow",
        )
        table.add_column("File:Line", style="cyan", no_wrap=True)
        table.add_column("Warning Message", style="dim")

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(item.get("file", ""), item.get("issue", ""))

        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        if not data:
            return "<h2>⚡ Cyclomatic Complexity Warnings (Lizard)</h2>\n<table>\n  <tr><th>File:Line</th><th>Warning Message</th></tr>\n  <tr><td colspan=\"2\">No data.</td></tr>\n</table>"

        items = data if top_n is None else data[:top_n]
        rows = []
        for item in items:
            rows.append(f"<tr><td>{item.get('file', '')}</td><td>{item.get('issue', '')}</td></tr>")
        rows_str = "\n    ".join(rows)

        return f"""  <h2>⚡ Cyclomatic Complexity Warnings (Lizard)</h2>
  <table>
    <tr><th>File:Line</th><th>Warning Message</th></tr>
    {rows_str}
  </table>"""
