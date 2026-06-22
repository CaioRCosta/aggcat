import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich import box

from src.base_tool import BaseTool


class GithubTool(BaseTool):
    @property
    def name(self) -> str:
        return "github"

    @property
    def description(self) -> str:
        return "Fetches issue and PR process metrics via the GitHub API."

    @property
    def requires_github(self) -> bool:
        return True

    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        from src.pipeline import _detect_github_slug
        slug = _detect_github_slug(repo_path)
        if not slug:
            return []

        token = os.environ.get("GITHUB_TOKEN", "")
        try:
            from github import Github
            gh = Github(token)
            repo = gh.get_repo(slug)

            now = datetime.now(timezone.utc)

            open_issues = list(repo.get_issues(state="open"))
            issue_ages = [
                (now - issue.created_at).days
                for issue in open_issues
                if issue.pull_request is None
            ]
            avg_issue_age = round(sum(issue_ages) / len(issue_ages), 1) if issue_ages else 0.0

            open_prs = repo.get_pulls(state="open").totalCount

            all_closed_prs = repo.get_pulls(state="closed")
            merged_30d = sum(
                1 for pr in all_closed_prs
                if pr.merged_at and (now - pr.merged_at).days <= 30
            )

            return [{
                "slug": slug,
                "open_issues": len(issue_ages),
                "avg_issue_age_days": avg_issue_age,
                "open_prs": open_prs,
                "merged_prs_30d": merged_30d,
            }]
        except Exception:
            return []

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        if not data:
            return
        item = data[0]
        table = Table(
            title=f"🐙 GitHub Process Metrics — {item['slug']}",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan",
        )
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        table.add_row("Open issues", str(item["open_issues"]))
        table.add_row("Avg issue age (days)", str(item["avg_issue_age_days"]))
        table.add_row("Open PRs", str(item["open_prs"]))
        table.add_row("Merged PRs (last 30d)", str(item["merged_prs_30d"]))
        console.print(table)

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        if not data:
            return (
                "<h2>🐙 GitHub Process Metrics</h2>\n"
                "<table><tr><th>Metric</th><th>Value</th></tr>"
                "<tr><td colspan=\"2\">No data.</td></tr></table>"
            )
        item = data[0]
        rows = (
            f"<tr><td>Open issues</td><td>{item['open_issues']}</td></tr>"
            f"<tr><td>Avg issue age (days)</td><td>{item['avg_issue_age_days']}</td></tr>"
            f"<tr><td>Open PRs</td><td>{item['open_prs']}</td></tr>"
            f"<tr><td>Merged PRs (last 30d)</td><td>{item['merged_prs_30d']}</td></tr>"
        )
        return (
            f"<h2>🐙 GitHub Process Metrics — {item['slug']}</h2>\n"
            f"<table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>"
        )
