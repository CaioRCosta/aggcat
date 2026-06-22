from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

from src.base_composite import CompositeReport
from src.tools.pydriller_tool import PyDrillerTool
from src.tools.lizard_tool import LizardTool

_PYDRILLER = PyDrillerTool()
_LIZARD = LizardTool()

class HotspotsReport(CompositeReport):
    @property
    def name(self) -> str:
        return "hotspots"

    @property
    def description(self) -> str:
        return "Files with high churn AND high complexity — highest refactoring risk."

    @property
    def defaults(self) -> Dict[str, Any]:
        return {"min_churn": 5, "min_cc": 10}

    @property
    def depends_on(self) -> List:
        return [_PYDRILLER, _LIZARD]

    def run(self, static: Dict[str, Any]) -> List[Dict[str, Any]]:
        min_churn = self._get_config("min_churn")
        min_cc = self._get_config("min_cc")
        churn = {r["file"]: r["churn"] for r in static.get("pydriller", [])}
        cc: Dict[str, int] = {}
        for r in static.get("lizard", []):
            filepath = r["file"].split(":")[0]
            cc[filepath] = max(cc.get(filepath, 0), _extract_cc(r["issue"]))

        results = []
        for filepath, churn_count in churn.items():
            norm = filepath.lstrip("./")
            match = next((p for p in cc if p.lstrip("./") == norm), None)
            if match is None:
                continue
            cc_val = cc[match]
            if churn_count >= min_churn and cc_val >= min_cc:
                results.append({"file": norm, "churn": churn_count, "cc": cc_val})

        results.sort(key=lambda x: x["churn"], reverse=True)
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="🔴 Hotspots — High Churn + High Complexity",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold red",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Churn", justify="right")
        table.add_column("CC", justify="right")
        table.add_column("Risk", justify="center")

        items = data if top_n is None else data[:top_n]
        for item in items:
            risk_color = "red" if item["cc"] >= 20 else "yellow"
            table.add_row(
                item["file"],
                str(item["churn"]),
                str(item["cc"]),
                Text("●", style=risk_color),
            )
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>🔴 Hotspots — High Churn + High Complexity</h2>\n"
                "<table><tr><th>File</th><th>Churn</th><th>CC</th></tr>"
                "<tr><td colspan=\"3\">No hotspots found.</td></tr></table>"
            )
        rows = "".join(
            f"<tr><td>{i['file']}</td><td>{i['churn']}</td><td>{i['cc']}</td></tr>"
            for i in items
        )
        return (
            "<h2>🔴 Hotspots — High Churn + High Complexity</h2>\n"
            "<table><tr><th>File</th><th>Churn</th><th>CC</th></tr>"
            f"{rows}</table>"
        )


def _extract_cc(issue_str: str) -> int:
    for part in issue_str.split(","):
        part = part.strip()
        if "CCN" in part:
            try:
                return int(part.split()[0])
            except (ValueError, IndexError):
                pass
    return 0
