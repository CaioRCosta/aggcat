from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

from src.base_composite import CompositeReport
from src.tools.gitpython_tool import GitPythonTool

_GITPYTHON = GitPythonTool()

class TruckFactorReport(CompositeReport):
    @property
    def name(self) -> str:
        return "truck_factor"

    @property
    def description(self) -> str:
        return "Files concentrated in few developers — bus factor risk."

    @property
    def defaults(self) -> Dict[str, Any]:
        return {"max_authors": 2}

    @property
    def depends_on(self) -> List:
        return [_GITPYTHON]

    def run(self, static: Dict[str, Any]) -> List[Dict[str, Any]]:
        max_authors = self._get_config("max_authors")
        results = [
            r for r in static.get("gitpython", [])
            if r["authors"] <= max_authors
        ]
        results.sort(key=lambda x: (x["authors"], -x["commits"]))
        return results

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        table = Table(
            title="🟡 Truck Factor Risk — Files Concentrated in Few Developers",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold yellow",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Authors", justify="right")
        table.add_column("Commits", justify="right")
        table.add_column("Risk", justify="center")

        items = data if top_n is None else data[:top_n]
        for item in items:
            color = "red" if item["authors"] == 1 else "yellow"
            table.add_row(
                item["file"],
                str(item["authors"]),
                str(item["commits"]),
                Text("●", style=color),
            )
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        items = data if top_n is None else data[:top_n]
        if not items:
            return (
                "<h2>🟡 Truck Factor Risk</h2>\n"
                "<table><tr><th>File</th><th>Authors</th><th>Commits</th></tr>"
                "<tr><td colspan=\"3\">No truck factor risk found.</td></tr></table>"
            )
        rows = "".join(
            f"<tr><td>{i['file']}</td><td>{i['authors']}</td><td>{i['commits']}</td></tr>"
            for i in items
        )
        return (
            "<h2>🟡 Truck Factor Risk</h2>\n"
            "<table><tr><th>File</th><th>Authors</th><th>Commits</th></tr>"
            f"{rows}</table>"
        )
