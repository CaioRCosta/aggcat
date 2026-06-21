from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AnalysisResult:
    repo_path: str
    static: dict = field(default_factory=dict)
    git: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def run(repo_path: str, github_repo: str | None = None) -> AnalysisResult:
    path = Path(repo_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Repository path not found: {path}")

    result = AnalysisResult(repo_path=str(path))

    from src.static import analyzer
    result.static = analyzer.run(path)

    # TODO
    # --- Git mining ---
    # from aggcat.git import miner
    # result.git = miner.run(path, github_repo=github_repo)

    return result
