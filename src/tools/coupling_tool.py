import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool

_SKIP_DIRS = {"venv", ".venv", "__pycache__", ".git", "node_modules"}


def _module_name(py_file: Path, repo_path: Path) -> str:
    rel = py_file.relative_to(repo_path)
    return ".".join(rel.with_suffix("").parts)


def _imported_modules(py_file: Path) -> List[str]:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


class CouplingTool(BaseTool):
    @property
    def name(self) -> str:
        return "coupling"

    @property
    def description(self) -> str:
        return "Measures module fan-in / fan-out via static import graph."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        py_files = [
            f for f in repo_path.rglob("*.py")
            if not any(part in _SKIP_DIRS for part in f.parts)
        ]
        known_modules = {_module_name(f, repo_path) for f in py_files}

        fan_out: dict = defaultdict(set)
        fan_in: dict = defaultdict(set)

        for py_file in py_files:
            module = _module_name(py_file, repo_path)
            for imported in _imported_modules(py_file):
                # only count internal imports
                if any(imported == km or imported.startswith(km + ".") for km in known_modules):
                    fan_out[module].add(imported)
                    fan_in[imported].add(module)

        all_modules = known_modules
        results = [
            {
                "module": m,
                "fan_out": len(fan_out[m]),
                "fan_in": len(fan_in[m]),
            }
            for m in all_modules
        ]
        results.sort(key=lambda x: x["fan_out"] + x["fan_in"], reverse=True)
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="🔗 Module Coupling (Fan-in / Fan-out)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold yellow",
        )
        table.add_column("Module", style="cyan")
        table.add_column("Fan-out", justify="right")
        table.add_column("Fan-in", justify="right")

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(item["module"], str(item["fan_out"]), str(item["fan_in"]))
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>🔗 Module Coupling (Fan-in / Fan-out)</h2>\n"
                "<table><tr><th>Module</th><th>Fan-out</th><th>Fan-in</th></tr>"
                "<tr><td colspan=\"3\">No data.</td></tr></table>"
            )
        rows = "".join(
            f"<tr><td>{i['module']}</td><td>{i['fan_out']}</td><td>{i['fan_in']}</td></tr>"
            for i in items
        )
        return (
            "<h2>🔗 Module Coupling (Fan-in / Fan-out)</h2>\n"
            "<table><tr><th>Module</th><th>Fan-out</th><th>Fan-in</th></tr>"
            f"{rows}</table>"
        )
