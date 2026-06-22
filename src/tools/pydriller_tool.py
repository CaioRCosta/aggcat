from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from pydriller import Repository

from src.base_tool import BaseTool

_SKIP_DIRS = {"venv", ".venv", "__pycache__", "node_modules"}


class PyDrillerTool(BaseTool):
    @property
    def name(self) -> str:
        return "pydriller"

    @property
    def description(self) -> str:
        return "Counts modification frequency (churn) per file via git history."

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        try:
            churn: Counter = Counter()
            for commit in Repository(str(repo_path)).traverse_commits():
                for f in commit.modified_files:
                    path = f.new_path or f.old_path
                    if not path:
                        continue
                    if any(part in _SKIP_DIRS for part in Path(path).parts):
                        continue
                    churn[path] += 1

            return [
                {"file": filepath, "churn": count}
                for filepath, count in churn.most_common()
            ]
        except Exception:
            return []
