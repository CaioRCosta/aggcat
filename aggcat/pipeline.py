"""Central pipeline that orchestrates all analysis tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AnalysisResult:
    """Unified container for all tool outputs."""

    repo_path: str
    static: dict = field(default_factory=dict)   # Pessoa 2 fills this
    git: dict = field(default_factory=dict)        # Pessoa 3 fills this
    errors: list[str] = field(default_factory=list)


def run(repo_path: str, github_repo: str | None = None) -> AnalysisResult:
    """
    Entry point called by the CLI.

    Parameters
    ----------
    repo_path:
        Absolute or relative path to a local Git repository.
    github_repo:
        Optional ``owner/repo`` string for GitHub API queries.

    Returns
    -------
    AnalysisResult
        Aggregated results from every tool.
    """
    path = Path(repo_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Repository path not found: {path}")

    result = AnalysisResult(repo_path=str(path))

    from aggcat.static import analyzer
    result.static = analyzer.run(path)

    # --- Git mining (Pessoa 3) ---
    # from aggcat.git import miner
    # result.git = miner.run(path, github_repo=github_repo)

    return result
