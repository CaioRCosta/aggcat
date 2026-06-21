"""aggcat — aggregate code analysis tools and metrics in one place."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from aggcat import pipeline, report

app = typer.Typer(
    name="aggcat",
    help="Aggregate code analysis tools and metrics in one place.",
    add_completion=False,
)
console = Console()


@app.command()
def analyze(
    repo: str = typer.Argument(..., help="Path to a local Git repository."),
    output: str = typer.Option(
        "terminal",
        "--output",
        "-o",
        help="Output format: terminal | json | html",
    ),
    github_repo: str = typer.Option(
        None,
        "--github-repo",
        "-g",
        help="GitHub repository in 'owner/repo' format for API metrics.",
    ),
    all_results: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all results instead of top 10.",
    ),
) -> None:
    """Run all analysis tools against a repository and display a unified report."""
    top_n = None if all_results else report.DEFAULT_TOP_N

    result = pipeline.run(repo, github_repo=github_repo)

    if output == "terminal":
        report.render_terminal(result, top_n=top_n)
    elif output == "json":
        report.render_json(result, top_n=top_n)
    elif output == "html":
        report.render_html(result, top_n=top_n)
    else:
        console.print(
            f"[red]Unknown output format '[bold]{output}[/bold]'. "
            "Choose from: terminal, json, html.[/red]"
        )
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show aggcat version."""
    from importlib.metadata import version as pkg_version  # noqa: PLC0415

    try:
        v = pkg_version("aggcat")
    except Exception:
        v = "dev"
    console.print(f"aggcat [bold]{v}[/bold]")


if __name__ == "__main__":
    app()