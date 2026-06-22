import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess


class PipAuditTool(BaseTool):
    @property
    def name(self) -> str:
        return "pip_audit"

    @property
    def description(self) -> str:
        return "Detects known CVEs in project dependencies using pip-audit."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        stdout = run_subprocess(["pip-audit", "--format", "json", "--progress-spinner", "off"])
        if not stdout:
            return []
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return []

        results = []
        for entry in data.get("dependencies", []):
            package = entry.get("name", "")
            version = entry.get("version", "")
            for vuln in entry.get("vulns", []):
                results.append({
                    "package": package,
                    "version": version,
                    "vuln_id": vuln.get("id", ""),
                    "description": vuln.get("description", ""),
                    "fix_versions": ", ".join(vuln.get("fix_versions", [])) or "—",
                })
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="🔒 Dependency Vulnerabilities (pip-audit)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold red",
        )
        table.add_column("Package", style="cyan")
        table.add_column("Version", justify="right")
        table.add_column("CVE / ID", style="red")
        table.add_column("Fix versions")
        table.add_column("Description", no_wrap=False)

        items = data if top_n is None else data[:top_n]
        for item in items:
            table.add_row(
                item["package"],
                item["version"],
                Text(item["vuln_id"], style="bold red"),
                item["fix_versions"],
                item["description"],
            )
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>🔒 Dependency Vulnerabilities (pip-audit)</h2>\n"
                "<table><tr><th>Package</th><th>Version</th><th>CVE / ID</th>"
                "<th>Fix versions</th><th>Description</th></tr>"
                "<tr><td colspan=\"5\">No vulnerabilities found.</td></tr></table>"
            )
        rows = "".join(
            f"<tr><td>{i['package']}</td><td>{i['version']}</td>"
            f"<td class='badge-high'>{i['vuln_id']}</td>"
            f"<td>{i['fix_versions']}</td><td>{i['description']}</td></tr>"
            for i in items
        )
        return (
            "<h2>🔒 Dependency Vulnerabilities (pip-audit)</h2>\n"
            "<table><tr><th>Package</th><th>Version</th><th>CVE / ID</th>"
            f"<th>Fix versions</th><th>Description</th></tr>{rows}</table>"
        )
