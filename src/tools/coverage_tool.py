import json
from pathlib import Path
from typing import Any, Dict, List

from src.base_tool import BaseTool
from src.tools.utils import run_subprocess


class CoverageTool(BaseTool):
    @property
    def name(self) -> str:
        return "coverage"

    @property
    def description(self) -> str:
        return "Reads line coverage per file from an existing .coverage file."

    @property
    def renderable(self) -> bool:
        return False

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        coverage_file = repo_path / ".coverage"
        if not coverage_file.exists():
            return []

        stdout = run_subprocess([
            "python", "-m", "coverage", "json",
            "--data-file", str(coverage_file),
            "-o", "-",
        ])
        if not stdout:
            return []
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return []

        results = []
        for filepath, stats in data.get("files", {}).items():
            summary = stats.get("summary", {})
            covered = summary.get("covered_lines", 0)
            total = summary.get("num_statements", 0)
            pct = round(covered / total * 100, 1) if total > 0 else 100.0
            results.append({
                "file": filepath,
                "coverage_pct": pct,
                "covered_lines": covered,
                "total_lines": total,
            })

        results.sort(key=lambda x: x["coverage_pct"])
        return results
