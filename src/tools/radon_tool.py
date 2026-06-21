import json
from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess
from src.config import load_config

class RadonTool(BaseTool):
    @property
    def name(self) -> str:
        return "radon"
    
    @property
    def description(self) -> str:
        return "Calculates the Maintainability Index (MI) for Python files using Radon."

    @property
    def defaults(self) -> Dict[str, Any]:
        return {
            "mi_grade_a": 80.0,
            "mi_grade_b": 60.0,
            "mi_grade_c": 40.0,
        }

    def _get_config(self, key: str) -> Any:
        user_config = load_config()
        return user_config.get(self.name, {}).get(key, self.defaults.get(key))

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        try:
            stdout = run_subprocess(["radon", "mi", "-j", "-i", "venv,.venv", str(repo_path)])
            if not stdout:
                return []
                
            data = json.loads(stdout)
            maintainability = []
            
            for filepath, details in data.items():
                mi_score = details.get("mi", 0.0)
                maintainability.append({
                    "file": filepath,
                    "mi": round(mi_score, 2)
                })
                
            maintainability.sort(key=lambda x: x["mi"])
            return maintainability
            
        except Exception:
            return []

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return

        mi_grade_a = self._get_config("mi_grade_a")
        mi_grade_b = self._get_config("mi_grade_b")
        mi_grade_c = self._get_config("mi_grade_c")

        table = Table(
            title="🟢 Maintainability Index",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold green",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("MI Score", justify="right")
        table.add_column("Grade", justify="center")

        items = data if top_n is None else data[:top_n]
        for item in items:
            mi = item.get("mi", 0.0)
            if mi >= mi_grade_a:
                grade = Text("A  ✓", style="green")
            elif mi >= mi_grade_b:
                grade = Text("B  ~", style="yellow")
            elif mi >= mi_grade_c:
                grade = Text("C  !", style="orange3")
            else:
                grade = Text("D  ✗", style="red")
            table.add_row(item.get("file", ""), f"{mi:.1f}", grade)

        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        if not data:
            return "<h2>🟢 Maintainability Index</h2>\n<table>\n  <tr><th>File</th><th>MI Score</th></tr>\n  <tr><td colspan=\"2\">No data.</td></tr>\n</table>"

        items = data if top_n is None else data[:top_n]
        rows = []
        for item in items:
            rows.append(f"<tr><td>{item.get('file', '')}</td><td>{item.get('mi', '')}</td></tr>")
        rows_str = "\n    ".join(rows)

        return f"""  <h2>🟢 Maintainability Index</h2>
  <table>
    <tr><th>File</th><th>MI Score</th></tr>
    {rows_str}
  </table>"""
