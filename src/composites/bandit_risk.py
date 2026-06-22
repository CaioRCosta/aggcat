from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

from src.base_composite import CompositeReport
from src.tools.bandit_tool import BanditTool
from src.tools.lizard_tool import LizardTool

_BANDIT = BanditTool()
_LIZARD = LizardTool()


def _extract_cc(issue_str: str) -> int:
    for part in issue_str.split(","):
        part = part.strip()
        if "CCN" in part:
            try:
                return int(part.split()[0])
            except (ValueError, IndexError):
                pass
    return 0


class BanditRiskReport(CompositeReport):
    @property
    def name(self) -> str:
        return "bandit_risk"

    @property
    def description(self) -> str:
        return "Security issues annotated with file complexity — harder-to-fix flaws first."

    @property
    def depends_on(self) -> List:
        return [_BANDIT, _LIZARD]

    def run(self, static: Dict[str, Any]) -> List[Dict[str, Any]]:
        cc: Dict[str, int] = {}
        for r in static.get("lizard", []):
            filepath = r["file"].split(":")[0].lstrip("./")
            cc[filepath] = max(cc.get(filepath, 0), _extract_cc(r["issue"]))

        results = []
        for finding in static.get("bandit", []):
            filepath = finding.get("file", "").lstrip("./")
            if "/tests/" in filepath or filepath.startswith("tests/"):
                continue
            cc_val = cc.get(filepath, 0)
            if cc_val == 0:
                continue
            results.append({**finding, "cc": cc_val})

        results.sort(key=lambda x: (x.get("severity", ""), x["cc"]), reverse=True)
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="🛡️  Security Issues × Complexity (Bandit Risk)",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold red",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Severity", justify="center")
        table.add_column("CC", justify="right")
        table.add_column("Issue")

        severity_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
        items = data if top_n is None else data[:top_n]
        for item in items:
            sev = item.get("severity", "")
            color = severity_color.get(sev, "white")
            table.add_row(
                item.get("file", ""),
                Text(sev, style=f"bold {color}"),
                str(item["cc"]),
                item.get("issue_text", ""),
            )
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>🛡️ Security Issues × Complexity (Bandit Risk)</h2>\n"
                "<table><tr><th>File</th><th>Severity</th><th>CC</th><th>Issue</th></tr>"
                "<tr><td colspan=\"4\">No security issues found.</td></tr></table>"
            )
        rows = "".join(
            "<tr><td>{}</td><td class='badge-{}'>{}</td><td>{}</td><td>{}</td></tr>".format(
                i.get("file", ""),
                i.get("severity", "").lower(),
                i.get("severity", ""),
                i["cc"],
                i.get("issue_text", ""),
            )
            for i in items
        )
        return (
            "<h2>🛡️ Security Issues × Complexity (Bandit Risk)</h2>\n"
            "<table><tr><th>File</th><th>Severity</th><th>CC</th><th>Issue</th></tr>"
            f"{rows}</table>"
        )
