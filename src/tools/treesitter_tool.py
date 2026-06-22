from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool

try:
    from tree_sitter import Language, Parser
    import tree_sitter_python as tspython
    _PY_LANG = Language(tspython.language())
    _PARSER = Parser(_PY_LANG)
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False

_SKIP_DIRS = {"venv", ".venv", "__pycache__", ".git", "node_modules"}

_PATTERNS = {
    "bare_except": "Bare `except:` catches everything including KeyboardInterrupt and SystemExit.",
    "broad_except_exception": "Catching `Exception` broadly suppresses unexpected errors.",
}


def _find_antipatterns(source: bytes) -> List[Dict[str, Any]]:
    tree = _PARSER.parse(source)
    findings = []

    def walk(node):
        if node.type == "except_clause":
            children_types = [c.type for c in node.children]
            # bare except: children are ['except', ':', 'block']
            if "identifier" not in children_types and "type" not in children_types:
                row = node.start_point[0] + 1
                findings.append({"pattern": "bare_except", "line": row})
            else:
                # check if it catches bare Exception (no `as` binding, just `except Exception:`)
                for child in node.children:
                    if child.type == "identifier" and child.text == b"Exception":
                        row = node.start_point[0] + 1
                        findings.append({"pattern": "broad_except_exception", "line": row})
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return findings


class TreesitterTool(BaseTool):
    @property
    def name(self) -> str:
        return "treesitter"

    @property
    def description(self) -> str:
        return "Detects anti-patterns (bare except, broad catches) via Tree-sitter AST."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        if not _AVAILABLE:
            return []

        results = []
        for py_file in repo_path.rglob("*.py"):
            if any(part in _SKIP_DIRS for part in py_file.parts):
                continue
            try:
                source = py_file.read_bytes()
            except OSError:
                continue
            rel = str(py_file.relative_to(repo_path))
            for finding in _find_antipatterns(source):
                results.append({
                    "file": rel,
                    "line": finding["line"],
                    "pattern": finding["pattern"],
                    "description": _PATTERNS[finding["pattern"]],
                })

        results.sort(key=lambda x: (x["file"], x["line"]))
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="🌳 Anti-patterns (Tree-sitter)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold magenta",
        )
        table.add_column("File:Line", style="cyan", no_wrap=True)
        table.add_column("Pattern", style="red")
        table.add_column("Description")

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(
                f"{item['file']}:{item['line']}",
                item["pattern"],
                item["description"],
            )
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>🌳 Anti-patterns (Tree-sitter)</h2>\n"
                "<table><tr><th>File:Line</th><th>Pattern</th><th>Description</th></tr>"
                "<tr><td colspan=\"3\">No anti-patterns found.</td></tr></table>"
            )
        rows = "".join(
            f"<tr><td>{i['file']}:{i['line']}</td>"
            f"<td class='badge-high'>{i['pattern']}</td>"
            f"<td>{i['description']}</td></tr>"
            for i in items
        )
        return (
            "<h2>🌳 Anti-patterns (Tree-sitter)</h2>\n"
            "<table><tr><th>File:Line</th><th>Pattern</th><th>Description</th></tr>"
            f"{rows}</table>"
        )
