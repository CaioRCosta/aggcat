import configparser
import re
from dataclasses import dataclass, field
from pathlib import Path

from src.base_composite import CompositeReport
from src.base_tool import BaseTool
from src.analyzer import ALL_BASE_TOOLS, SELECTABLE, COMPOSITE_REPORTS, _has_github_token
from src import analyzer


@dataclass
class AnalysisResult:
    repo_path: str
    github_slug: str | None = None
    static: dict = field(default_factory=dict)
    composite: dict = field(default_factory=dict)
    git: dict = field(default_factory=dict)
    selected_renderables: list = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _detect_github_slug(repo_path: Path) -> str | None:
    git_config = repo_path / ".git" / "config"
    if not git_config.exists():
        return None
    cfg = configparser.ConfigParser()
    cfg.read(git_config)
    url = cfg.get('remote "origin"', "url", fallback=None)
    if not url:
        return None
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def run(repo_path: str, selected: list = None, on_progress=None) -> AnalysisResult:
    path = Path(repo_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Repository path not found: {path}")

    result = AnalysisResult(repo_path=str(path), github_slug=_detect_github_slug(path))

    if selected is None:
        selected = SELECTABLE

    has_token = _has_github_token()
    selected = [s for s in selected if not s.requires_github or has_token]

    base_selected = [s for s in selected if isinstance(s, BaseTool)]
    composite_selected = [s for s in selected if isinstance(s, CompositeReport)]

    selected_names = {t.name for t in base_selected}
    dep_tools = [t for c in composite_selected for t in c.depends_on if t.name not in selected_names]

    result.static = analyzer.run(path, selected_tools=base_selected + dep_tools, on_progress=on_progress)

    for composite in composite_selected:
        if all(t.name in result.static for t in composite.depends_on):
            if on_progress:
                on_progress(composite.name)
            result.composite[composite.name] = composite.run(result.static)

    result.selected_renderables = selected
    return result
