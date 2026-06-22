import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from src.pipeline import AnalysisResult
from src.base_tool import BaseTool
from src.base_composite import CompositeReport

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


def render_terminal(result: AnalysisResult, top_n: int | None = None) -> None:
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]aggcat[/bold cyan] report — [green]{result.repo_path}[/green]",
            border_style="cyan",
        )
    )
    console.print()

    static = result.static
    renderables = result.selected_renderables
    base_tools = [t for t in renderables if isinstance(t, BaseTool)]
    composites = [t for t in renderables if isinstance(t, CompositeReport)]

    has_data = (
        any(static.get(t.name) for t in base_tools)
        or any(result.composite.get(c.name) for c in composites)
    )

    if not has_data:
        console.print("[dim]No data available yet. Make sure the analysis modules are connected.[/dim]")
    else:
        for tool in base_tools:
            tool_data = static.get(tool.name, [])
            if tool_data:
                console.print()
                tool.render_terminal(tool_data, console, top_n)

        for composite in composites:
            composite_data = result.composite.get(composite.name, [])
            if composite_data:
                console.print()
                composite.render_terminal(composite_data, console, top_n)

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
        "composite": result.composite,
        "git": result.git,
        "errors": result.errors,
    }

    if top_n is not None:
        for section in ("hotspots", "truck_factor"):
            if section in data["git"]:
                data["git"][section] = data["git"][section][:top_n]
        for key in data["static"]:
            data["static"][key] = data["static"][key][:top_n]
        for key in data["composite"]:
            data["composite"][key] = data["composite"][key][:top_n]

    output = json.dumps(data, indent=2, ensure_ascii=False)
    console.print(output)
    _ask_save(output, "aggcat-report.json")


# HTML report


def _build_html(result: AnalysisResult, top_n: int | None) -> str:
    static = result.static

    html_parts = []
    for item in result.selected_renderables:
        if isinstance(item, BaseTool):
            html_parts.append(item.render_html_section(static.get(item.name, []), top_n))
        elif isinstance(item, CompositeReport):
            html_parts.append(item.render_html_section(result.composite.get(item.name, []), top_n))

    sections_html = "\n\n".join(p for p in html_parts if p)

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

  {sections_html}

  {top_note}
</body>
</html>"""


def render_html(result: AnalysisResult, top_n: int | None = None) -> None:
    html = _build_html(result, top_n)
    console.print("[dim]HTML report generated.[/dim]")
    _ask_save(html, "aggcat-report.html")