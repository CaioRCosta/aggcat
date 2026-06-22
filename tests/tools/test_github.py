from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from rich.console import Console

from src.tools.github_tool import GithubTool


def _make_issue(days_old, is_pr=False):
    issue = MagicMock()
    issue.created_at = datetime.now(timezone.utc) - timedelta(days=days_old)
    issue.pull_request = MagicMock() if is_pr else None
    return issue


def _make_pr(merged_days_ago=None):
    pr = MagicMock()
    if merged_days_ago is not None:
        pr.merged_at = datetime.now(timezone.utc) - timedelta(days=merged_days_ago)
    else:
        pr.merged_at = None
    return pr


@patch("src.tools.github_tool.GithubTool.run")
def test_run_returns_empty_without_slug(mock_run, tmp_path):
    mock_run.return_value = []
    result = GithubTool().run(tmp_path)
    assert result == []


def test_requires_github():
    assert GithubTool().requires_github is True


@patch("src.pipeline._detect_github_slug", return_value="owner/repo")
@patch("github.Github")
def test_run_parses_metrics(mock_github_cls, mock_slug, tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token123")

    repo = MagicMock()
    repo.get_issues.return_value = [
        _make_issue(10),
        _make_issue(20),
        _make_issue(5, is_pr=True),
    ]
    repo.get_pulls.return_value.totalCount = 3
    repo.get_pulls.return_value.__iter__ = lambda self: iter([
        _make_pr(merged_days_ago=5),
        _make_pr(merged_days_ago=40),
    ])
    mock_github_cls.return_value.get_repo.return_value = repo

    result = GithubTool().run(tmp_path)

    assert len(result) == 1
    assert result[0]["slug"] == "owner/repo"
    assert result[0]["open_issues"] == 2
    assert result[0]["avg_issue_age_days"] == 15.0
    assert result[0]["open_prs"] == 3
    assert result[0]["merged_prs_30d"] == 1


@patch("src.pipeline._detect_github_slug", return_value="owner/repo")
@patch("github.Github", side_effect=Exception("API error"))
def test_run_exception_returns_empty(mock_cls, mock_slug, tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    assert GithubTool().run(tmp_path) == []


def test_render_terminal_empty_does_not_print():
    from unittest.mock import MagicMock
    console = MagicMock()
    GithubTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"slug": "owner/repo", "open_issues": 5, "avg_issue_age_days": 12.0, "open_prs": 2, "merged_prs_30d": 4}]
    GithubTool().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "owner/repo" in out
    assert "5" in out


def test_render_html_empty():
    assert "No data." in GithubTool().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"slug": "owner/repo", "open_issues": 5, "avg_issue_age_days": 12.0, "open_prs": 2, "merged_prs_30d": 4}]
    html = GithubTool().render_html_section(data, top_n=10)
    assert "owner/repo" in html
    assert "12.0" in html
