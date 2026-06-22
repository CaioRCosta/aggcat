import ast
from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool
from src.config import load_config

class NestingDepthVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def _visit_nested(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_If(self, node): self._visit_nested(node)
    def visit_For(self, node): self._visit_nested(node)
    def visit_While(self, node): self._visit_nested(node)
    def visit_Try(self, node): self._visit_nested(node)
    def visit_With(self, node): self._visit_nested(node)

class AstNestingTool(BaseTool):
    @property
    def name(self) -> str:
        return "ast_nesting"
    
    @property
    def description(self) -> str:
        return "Detects deep control nesting in Python files using AST analysis."

    @property
    def defaults(self) -> Dict[str, Any]:
        return {
            "max_depth": 3,
        }

    def _get_config(self, key: str) -> Any:
        user_config = load_config()
        return user_config.get(self.name, {}).get(key, self.defaults.get(key))

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        max_depth = self._get_config("max_depth")
        
        issues = []
        for py_file in repo_path.rglob("*.py"):
            if "venv" in py_file.parts or ".venv" in py_file.parts:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                visitor = NestingDepthVisitor()
                visitor.visit(tree)
                
                if visitor.max_depth > max_depth:
                    rel_path = py_file.relative_to(repo_path)
                    issues.append({
                        "file": str(rel_path),
                        "issue": f"Deep nesting detected (depth: {visitor.max_depth})"
                    })
            except Exception:
                continue
                
        return issues

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return

        table = Table(
            title="🔍 Deep Control Nesting (AST)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold magenta",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Nesting Issue", style="dim")

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(item.get("file", ""), item.get("issue", ""))

        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        if not data:
            return "<h2>🔍 Deep Control Nesting (AST)</h2>\n<table>\n  <tr><th>File</th><th>Nesting Issue</th></tr>\n  <tr><td colspan=\"2\">No data.</td></tr>\n</table>"

        items = data if top_n is None else data[:top_n]
        rows = []
        for item in items:
            rows.append(f"<tr><td>{item.get('file', '')}</td><td>{item.get('issue', '')}</td></tr>")
        rows_str = "\n    ".join(rows)

        return f"""  <h2>🔍 Deep Control Nesting (AST)</h2>
  <table>
    <tr><th>File</th><th>Nesting Issue</th></tr>
    {rows_str}
  </table>"""
