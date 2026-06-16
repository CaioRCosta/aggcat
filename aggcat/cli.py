"""aggcat — aggregate code analysis tools and metrics in one place."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

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
) -> None:
    """Run all analysis tools against a repository and display a unified report."""
    console.print(
        Panel.fit(
            f"[bold cyan]aggcat[/bold cyan] — analysing [green]{repo}[/green]",
            border_style="cyan",
        )
    )

    # TODO: Pessoa 2 — plug static analysis pipeline here (pipeline.run_static)
    # TODO: Pessoa 3 — plug git mining pipeline here (pipeline.run_git)

    console.print(f"[yellow]Output format:[/yellow] {output}")
    if github_repo:
        console.print(f"[yellow]GitHub repo:[/yellow] {github_repo}")

    console.print("[bold green]✓ Analysis complete.[/bold green]")


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
