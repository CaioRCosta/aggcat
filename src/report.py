import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

from src.pipeline import AnalysisResult

console = Console()

DEFAULT_TOP_N = 10

# Helpers

def _severity_color(value: float, low: float, high: float) -> str:
    if value <= low:
        return "green"
    if value <= high:
        return "yellow"
    return "red"


def _top(items: list, n: int | None) -> list:
    return items if n is None else items[:n]


def _ask_save(data: str, default_filename: str) -> None:
    answer = console.input(
        f"\n[bold]Save to file?[/bold] Y/n: "
    ).strip().lower()
    if answer == "y" or answer == "":
        filename = console.input(
            f"[bold]Filename[/bold] [dim](press Enter for '{default_filename}')[/dim]: "
        ).strip()
        if not filename:
            filename = default_filename
        Path(filename).write_text(data, encoding="utf-8")
        console.print(f"[green]✓ Saved to {filename}[/green]")


# Terminal report


def _render_hotspots(hotspots: list[dict], top_n: int | None) -> None:
    """Render hotspots table (high churn + high complexity)."""
    if not hotspots:
        return

    table = Table(
        title="🔴 Hotspots — High Churn + High Complexity",
        box=box.ROUNDED,
        show_lines=True,
        title_style="bold red",
    )
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Churn", justify="right")
    table.add_column("Cyclomatic Complexity", justify="right")
    table.add_column("Risk", justify="center")

    for item in _top(hotspots, top_n):
        churn = item.get("churn", 0)
        cc = item.get("complexity", 0)
        color = _severity_color(cc, 10, 20)
        risk = Text("●", style=color)
        table.add_row(item.get("file", ""), str(churn), str(cc), risk)

    console.print(table)


def _render_truck_factor(truck: list[dict], top_n: int | None) -> None:
    """Render truck factor table (files owned by few authors)."""
    if not truck:
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

    for item in _top(truck, top_n):
        authors = item.get("authors", 0)
        commits = item.get("commits", 0)
        color = _severity_color(authors, 2, 4)
        # invert: fewer authors = higher risk
        color = "red" if authors <= 1 else ("yellow" if authors <= 2 else "green")
        risk = Text("●", style=color)
        table.add_row(item.get("file", ""), str(authors), str(commits), risk)

    console.print(table)


# Dynamic Static Tools Terminal/HTML Rendering

def render_terminal(result: AnalysisResult, top_n: int | None = None) -> None:
    """Render the full report to the terminal."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]aggcat[/bold cyan] report — [green]{result.repo_path}[/green]",
            border_style="cyan",
        )
    )
    console.print()

    static = result.static
    git = result.git

    hotspots = git.get("hotspots", [])
    truck = git.get("truck_factor", [])

    from src.analyzer import TOOLS

    # Check if there is any data
    has_data = any([hotspots, truck]) or any(static.get(tool.name) for tool in TOOLS)

    if not has_data:
        console.print("[dim]No data available yet. Make sure the analysis modules are connected.[/dim]")
    else:
        _render_hotspots(hotspots, top_n)
        console.print()
        _render_truck_factor(truck, top_n)
        
        for tool in TOOLS:
            tool_data = static.get(tool.name, [])
            if tool_data:
                console.print()
                tool.render_terminal(tool_data, console, top_n)

    if top_n is not None:
        console.print(
            f"\n[dim]Showing top {top_n} results per section. "
            "Run with [bold]--all[/bold] to see everything.[/dim]"
        )


# JSON report


def render_json(result: AnalysisResult, top_n: int | None = None) -> None:
    data: dict[str, Any] = {
        "repo": result.repo_path,
        "static": result.static,
        "git": result.git,
        "errors": result.errors,
    }

    if top_n is not None:
        for section in ("hotspots", "truck_factor"):
            if section in data["git"]:
                data["git"][section] = data["git"][section][:top_n]
        
        from src.analyzer import TOOLS
        for tool in TOOLS:
            if tool.name in data["static"]:
                data["static"][tool.name] = data["static"][tool.name][:top_n]

    output = json.dumps(data, indent=2, ensure_ascii=False)
    console.print(output)
    _ask_save(output, "aggcat-report.json")


# HTML report


def _build_html(result: AnalysisResult, top_n: int | None) -> str:
    static = result.static
    git = result.git

    def rows(items: list[dict], keys: list[str]) -> str:
        out = []
        for item in _top(items, top_n):
            cells = "".join(f"<td>{item.get(k, '')}</td>" for k in keys)
            out.append(f"<tr>{cells}</tr>")
        return "\n".join(out)

    hotspot_rows = rows(
        git.get("hotspots", []), ["file", "churn", "complexity"]
    )
    truck_rows = rows(
        git.get("truck_factor", []), ["file", "authors", "commits"]
    )

    from src.analyzer import TOOLS
    static_html_parts = []
    for tool in TOOLS:
        tool_data = static.get(tool.name, [])
        static_html_parts.append(tool.render_html_section(tool_data, top_n))
    
    static_html = "\n\n".join(static_html_parts)

    top_note = (
        f"<p class='note'>Showing top {top_n} results. "
        "Re-run with <code>--all</code> to see everything.</p>"
        if top_n else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>aggcat report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; color: #1a1a2e; }}
    h1 {{ color: #0f3460; }}
    h2 {{ margin-top: 2rem; border-bottom: 2px solid #e0e0e0; padding-bottom: .3rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th {{ background: #0f3460; color: white; padding: .5rem 1rem; text-align: left; }}
    td {{ padding: .4rem 1rem; border-bottom: 1px solid #e0e0e0; }}
    tr:hover td {{ background: #f0f4ff; }}
    .note {{ color: #888; font-size: .9rem; margin-top: 2rem; }}
    .badge-high {{ color: #c0392b; font-weight: bold; }}
    .badge-medium {{ color: #e67e22; font-weight: bold; }}
    .badge-low {{ color: #27ae60; }}
  </style>
</head>
<body>
  <h1>aggcat report</h1>
  <p><strong>Repository:</strong> {result.repo_path}</p>

  <h2>🔴 Hotspots</h2>
  <table>
    <tr><th>File</th><th>Churn</th><th>Cyclomatic Complexity</th></tr>
    {hotspot_rows or '<tr><td colspan="3">No data.</td></tr>'}
  </table>

  <h2>🟡 Truck Factor Risk</h2>
  <table>
    <tr><th>File</th><th>Authors</th><th>Commits</th></tr>
    {truck_rows or '<tr><td colspan="3">No data.</td></tr>'}
  </table>

  {static_html}

  {top_note}
</body>
</html>"""


def render_html(result: AnalysisResult, top_n: int | None = None) -> None:
    html = _build_html(result, top_n)
    console.print("[dim]HTML report generated.[/dim]")
    _ask_save(html, "aggcat-report.html")