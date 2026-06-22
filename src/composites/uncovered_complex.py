from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

from src.base_composite import CompositeReport
from src.tools.coverage_tool import CoverageTool
from src.tools.lizard_tool import LizardTool

_COVERAGE = CoverageTool()
_LIZARD = LizardTool()

_COVERAGE_THRESHOLD = 60.0
_CC_THRESHOLD = 10


def _extract_cc(issue_str: str) -> int:
    for part in issue_str.split(","):
        part = part.strip()
        if "CCN" in part:
            try:
                return int(part.split()[0])
            except (ValueError, IndexError):
                pass
    return 0


class UncoveredComplexReport(CompositeReport):
    @property
    def name(self) -> str:
        return "uncovered_complex"

    @property
    def description(self) -> str:
        return "Complex files with low test coverage — highest risk to change."

    @property
    def depends_on(self) -> List:
        return [_COVERAGE, _LIZARD]

    def run(self, static: Dict[str, Any]) -> List[Dict[str, Any]]:
        coverage = {r["file"].lstrip("./"): r["coverage_pct"] for r in static.get("coverage", [])}

        cc: Dict[str, int] = {}
        for r in static.get("lizard", []):
            filepath = r["file"].split(":")[0].lstrip("./")
            cc[filepath] = max(cc.get(filepath, 0), _extract_cc(r["issue"]))

        results = []
        for filepath, cc_val in cc.items():
            cov = coverage.get(filepath)
            if cov is None:
                continue
            if cov < _COVERAGE_THRESHOLD and cc_val >= _CC_THRESHOLD:
                results.append({"file": filepath, "coverage_pct": cov, "cc": cc_val})

        results.sort(key=lambda x: x["cc"], reverse=True)
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="⚠️  Uncovered Complex Files",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold yellow",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Coverage", justify="right")
        table.add_column("CC", justify="right")
        table.add_column("Risk", justify="center")

        items = data if top_n is None else data[:top_n]
        for item in items:
            risk_color = "red" if item["coverage_pct"] < 30 else "yellow"
            table.add_row(
                item["file"],
                f"{item['coverage_pct']}%",
                str(item["cc"]),
                Text("●", style=risk_color),
            )
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>⚠️ Uncovered Complex Files</h2>\n"
                "<table><tr><th>File</th><th>Coverage</th><th>CC</th></tr>"
                "<tr><td colspan=\"3\">No uncovered complex files found.</td></tr></table>"
            )
        rows = "".join(
            f"<tr><td>{i['file']}</td><td>{i['coverage_pct']}%</td><td>{i['cc']}</td></tr>"
            for i in items
        )
        return (
            "<h2>⚠️ Uncovered Complex Files</h2>\n"
            "<table><tr><th>File</th><th>Coverage</th><th>CC</th></tr>"
            f"{rows}</table>"
        )
