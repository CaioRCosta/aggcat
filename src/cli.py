import sys
import typer
from rich.console import Console

from src import pipeline, report

try:
    import tty
    import termios
except ImportError:
    tty = None
    termios = None

app = typer.Typer(
    name="aggcat",
    help="Aggregate code analysis tools and metrics in one place.",
    add_completion=False,
)
console = Console()


def get_char() -> str:
    if tty is None or termios is None or not sys.stdin.isatty():
        # Fallback if not interactive/not tty
        char = sys.stdin.read(1)
        return char
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def select_tools_interactive() -> list:
    from src.analyzer import TOOLS
    if not sys.stdin.isatty():
        return TOOLS

    selected = [True] * len(TOOLS)
    current_idx = 0

    console.print("[bold cyan]Select tools to run (Arrow Keys to navigate, Space to toggle, Enter to confirm):[/bold cyan]\n")

    def render_menu():
        for i, tool in enumerate(TOOLS):
            if selected[i]:
                chk = "[bold green]✔[/bold green]"
                desc_style = "white"
            else:
                chk = "[dim]✗[/dim]"
                desc_style = "dim"

            if i == current_idx:
                cursor = "[bold cyan]> [/bold cyan]"
                name_style = "bold cyan"
            else:
                cursor = "  "
                name_style = "bold white" if selected[i] else "dim"

            console.print(f"{cursor}[{chk}] [{name_style}]{tool.name:<15}[/{name_style}] - [style={desc_style}]{tool.description}[/style]")

    try:
        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        while True:
            render_menu()
            ch = get_char()

            # Clear menu lines
            for _ in range(len(TOOLS)):
                sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()

            if ch == '\x1b[A': # Up
                current_idx = (current_idx - 1) % len(TOOLS)
            elif ch == '\x1b[B': # Down
                current_idx = (current_idx + 1) % len(TOOLS)
            elif ch == ' ': # Space
                selected[current_idx] = not selected[current_idx]
            elif ch in ('\r', '\n'): # Enter
                break
            elif ch == '\x03': # Ctrl+C
                raise KeyboardInterrupt()
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        console.print("[red]Aborted.[/red]")
        sys.exit(1)
    finally:
        # Show cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    chosen = [tool for i, tool in enumerate(TOOLS) if selected[i]]
    if not chosen:
        console.print("[red]Error: You must select at least one tool to run.[/red]")
        raise typer.Exit(code=1)

    return chosen


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
    top_n = None if all_results else report.DEFAULT_TOP_N

    selected_tools = None
    if not all_results:
        selected_tools = select_tools_interactive()

    result = pipeline.run(repo, github_repo=github_repo, selected_tools=selected_tools)

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
    from importlib.metadata import version as pkg_version

    try:
        v = pkg_version("aggcat")
    except Exception:
        v = "dev"
    console.print(f"aggcat [bold]{v}[/bold]")


if __name__ == "__main__":
    app()