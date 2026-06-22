import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess


class ClocTool(BaseTool):
    @property
    def name(self) -> str:
        return "cloc"

    @property
    def description(self) -> str:
        return "Counts code vs comment lines per file using cloc."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        stdout = run_subprocess([
            "cloc", "--json", "--by-file",
            "--exclude-dir=venv,.venv,__pycache__,.git",
            str(repo_path),
        ])
        if not stdout:
            return []
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return []

        results = []
        for filepath, stats in data.items():
            if filepath in ("header", "SUM"):
                continue
            code = stats.get("code", 0)
            comments = stats.get("comment", 0)
            total = code + comments
            ratio = round(comments / total, 2) if total > 0 else 0.0
            results.append({
                "file": filepath,
                "code_lines": code,
                "comment_lines": comments,
                "comment_ratio": ratio,
            })

        results.sort(key=lambda x: x["code_lines"], reverse=True)
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="📄 Code vs Comment Volume (Cloc)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold blue",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Code", justify="right")
        table.add_column("Comments", justify="right")
        table.add_column("Comment Ratio", justify="right")

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(
                item["file"],
                str(item["code_lines"]),
                str(item["comment_lines"]),
                f"{item['comment_ratio']:.0%}",
            )
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>📄 Code vs Comment Volume (Cloc)</h2>\n"
                "<table><tr><th>File</th><th>Code</th><th>Comments</th><th>Comment Ratio</th></tr>"
                "<tr><td colspan=\"4\">No data.</td></tr></table>"
            )
        rows = "".join(
            f"<tr><td>{i['file']}</td><td>{i['code_lines']}</td>"
            f"<td>{i['comment_lines']}</td><td>{i['comment_ratio']:.0%}</td></tr>"
            for i in items
        )
        return (
            "<h2>📄 Code vs Comment Volume (Cloc)</h2>\n"
            "<table><tr><th>File</th><th>Code</th><th>Comments</th><th>Comment Ratio</th></tr>"
            f"{rows}</table>"
        )
