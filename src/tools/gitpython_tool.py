from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

import git

from src.base_tool import BaseTool

_SKIP_DIRS = {"venv", ".venv", "__pycache__", "node_modules"}


class GitPythonTool(BaseTool):
    @property
    def name(self) -> str:
        return "gitpython"

    @property
    def description(self) -> str:
        return "Maps unique authors and commit counts per file (truck factor input)."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        try:
            repo = git.Repo(str(repo_path))
            authors_per_file: dict = defaultdict(set)
            commits_per_file: Counter = defaultdict(int)

            for commit in repo.iter_commits():
                for filepath in commit.stats.files:
                    if any(part in _SKIP_DIRS for part in Path(filepath).parts):
                        continue
                    authors_per_file[filepath].add(commit.author.email)
                    commits_per_file[filepath] += 1

            results = [
                {
                    "file": filepath,
                    "authors": len(authors_per_file[filepath]),
                    "commits": commits_per_file[filepath],
                }
                for filepath in authors_per_file
            ]
            results.sort(key=lambda x: x["authors"])
            return results
        except Exception:
            return []
