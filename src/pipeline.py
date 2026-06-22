import configparser
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AnalysisResult:
    repo_path: str
    github_slug: str | None = None
    static: dict = field(default_factory=dict)
    git: dict = field(default_factory=dict)
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
    # git@github.com:owner/repo.git  or  https://github.com/owner/repo.git
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def run(repo_path: str, selected_tools: list = None) -> AnalysisResult:
    path = Path(repo_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Repository path not found: {path}")

    result = AnalysisResult(repo_path=str(path), github_slug=_detect_github_slug(path))

    from src import analyzer
    result.static = analyzer.run(path, selected_tools=selected_tools)

    return result
