import sys
from importlib.metadata import version as pkg_version
from io import StringIO
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from src import pipeline, report
from src.config import load_config, save_config, reset_config
from src.analyzer import TOOLS, SELECTABLE, ALL_BASE_TOOLS, COMPOSITE_REPORTS, _has_github_token
from src.base_composite import CompositeReport

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

config_app = typer.Typer(
    name="config",
    help="Manage tool configuration constants.",
    add_completion=False,
)
app.add_typer(config_app)


@config_app.command("show")
def config_show() -> None:
    """Show the current configuration for all tools."""
    user_config = load_config()
    console.print("[bold cyan]Current Tool Configurations:[/bold cyan]")
    for tool in TOOLS:
        if not getattr(tool, "defaults", None):
            continue
        console.print(f"\n[bold green]{tool.name}:[/bold green] - {tool.description}")
        tool_user = user_config.get(tool.name, {})
        for k, default_val in tool.defaults.items():
            val = tool_user.get(k, default_val)
            console.print(f"  {k} = {val} [dim](default: {default_val})[/dim]")


@config_app.command("set")
def config_set(
    tool: str = typer.Argument(..., help="The tool name."),
    key: str = typer.Argument(..., help="The config key to set."),
    value: str = typer.Argument(..., help="The value to set (will be cast dynamically to float/int/str)."),
) -> None:
    """Set a configuration constant for a tool."""
    # Find the tool in the registry
    target_tool = next((t for t in TOOLS if t.name == tool), None)
    if not target_tool or not getattr(target_tool, "defaults", None):
        console.print(f"[red]Error: Tool '{tool}' is not configurable.[/red]")
        raise typer.Exit(code=1)
        
    if key not in target_tool.defaults:
        console.print(f"[red]Error: Key '{key}' is not configurable for tool '{tool}'.[/red]")
        raise typer.Exit(code=1)

    default_val = target_tool.defaults[key]
    try:
        if isinstance(default_val, float):
            typed_val = float(value)
        elif isinstance(default_val, int):
            typed_val = int(value)
        else:
            typed_val = value
    except ValueError:
        console.print(f"[red]Error: Value '{value}' could not be cast to the type of '{key}' ({type(default_val).__name__}).[/red]")
        raise typer.Exit(code=1)

    user_config = load_config()
    if tool not in user_config:
        user_config[tool] = {}
    user_config[tool][key] = typed_val
    save_config(user_config)
    console.print(f"[green]✓ Config updated: {tool}.{key} = {typed_val}[/green]")


@config_app.command("reset")
def config_reset() -> None:
    """Reset configuration to defaults."""
    reset_config()
    console.print("[green]✓ Configuration reset to defaults.[/green]")



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
    if not sys.stdin.isatty():
        return [t for t in SELECTABLE if not t.requires_github or _has_github_token()]

    has_token = _has_github_token()
    unavailable = [t.requires_github and not has_token for t in SELECTABLE]
    selected = [not u for u in unavailable]
    current_idx = 0

    console.print("[bold cyan]Select tools to run (Arrow Keys to navigate, Space to toggle, Enter to confirm):[/bold cyan]\n")

    buf_console = Console(file=StringIO(), highlight=False)

    def render_menu():
        buf = StringIO()
        c = Console(file=buf, highlight=False, force_terminal=True)
        for i, tool in enumerate(SELECTABLE):
            desc = tool.full_description if isinstance(tool, CompositeReport) else tool.description
            if unavailable[i]:
                cursor = "  "
                chk = "[dim]–[/dim]"
                name_style = "dim"
                suffix = f"[dim]{desc} [red](requires GITHUB_TOKEN)[/red][/dim]"
            else:
                chk = "[bold green]✔[/bold green]" if selected[i] else "[dim]✗[/dim]"
                desc_style = "white" if selected[i] else "dim"
                cursor = "[bold cyan]> [/bold cyan]" if i == current_idx else "  "
                name_style = ("bold cyan" if i == current_idx
                              else "bold white" if selected[i] else "dim")
                suffix = f"[style={desc_style}]{desc}[/style]"
            c.print(f"{cursor}[{chk}] [{name_style}]{tool.name:<15}[/{name_style}] - {suffix}")
        sys.stdout.write(buf.getvalue())
        sys.stdout.flush()

    try:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        while True:
            render_menu()
            ch = get_char()

            # move cursor up and clear all menu lines in one write
            sys.stdout.write(("\033[F\033[K") * len(SELECTABLE))
            sys.stdout.flush()

            if ch == '\x1b[A':  # Up
                current_idx = (current_idx - 1) % len(SELECTABLE)
            elif ch == '\x1b[B':  # Down
                current_idx = (current_idx + 1) % len(SELECTABLE)
            elif ch == ' ':  # Space — ignore unavailable tools
                if not unavailable[current_idx]:
                    selected[current_idx] = not selected[current_idx]
            elif ch in ('\r', '\n'):  # Enter
                break
            elif ch == '\x03':  # Ctrl+C
                raise KeyboardInterrupt()
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        console.print("[red]Aborted.[/red]")
        sys.exit(1)
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    chosen = [tool for i, tool in enumerate(SELECTABLE) if selected[i]]
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
    top_n: int = typer.Option(
        None,
        "--top-n",
        "-n",
        help="Limit results to top N items per section. Shows all results by default.",
    ),
    all_tools: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Run all tools without the interactive selector.",
    ),
) -> None:
    selected = SELECTABLE if all_tools else select_tools_interactive()

    total = len(selected)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[dim]{task.fields[tool]}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Analyzing...", total=total, tool="")

        def on_progress(tool_name: str) -> None:
            progress.update(task, advance=1, tool=tool_name)

        result = pipeline.run(repo, selected=selected, on_progress=on_progress)

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
    try:
        v = pkg_version("aggcat")
    except Exception:
        v = "dev"
    console.print(f"aggcat [bold]{v}[/bold]")


if __name__ == "__main__":
    app()