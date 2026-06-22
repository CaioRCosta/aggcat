from unittest.mock import patch, MagicMock

from src.tools.gitpython_tool import GitPythonTool


def _make_repo(commits_data):
    repo = MagicMock()
    commits = []
    for author_email, files in commits_data:
        c = MagicMock()
        c.author.email = author_email
        c.stats.files = {f: {} for f in files}
        commits.append(c)
    repo.iter_commits.return_value = commits
    return repo


@patch("src.tools.gitpython_tool.git.Repo")
def test_run_counts_authors_and_commits(mock_repo_cls, tmp_path):
    mock_repo_cls.return_value = _make_repo([
        ("a@x.com", ["src/foo.py"]),
        ("b@x.com", ["src/foo.py"]),
        ("a@x.com", ["src/bar.py"]),
    ])
    result = GitPythonTool().run(tmp_path)
    by_file = {r["file"]: r for r in result}
    assert by_file["src/foo.py"]["authors"] == 2
    assert by_file["src/foo.py"]["commits"] == 2
    assert by_file["src/bar.py"]["authors"] == 1
    assert by_file["src/bar.py"]["commits"] == 1


@patch("src.tools.gitpython_tool.git.Repo")
def test_run_skips_venv(mock_repo_cls, tmp_path):
    mock_repo_cls.return_value = _make_repo([
        ("a@x.com", ["venv/lib/x.py", "src/ok.py"]),
    ])
    result = GitPythonTool().run(tmp_path)
    assert all("venv" not in r["file"] for r in result)


@patch("src.tools.gitpython_tool.git.Repo")
def test_run_sorts_by_authors_ascending(mock_repo_cls, tmp_path):
    mock_repo_cls.return_value = _make_repo([
        ("a@x.com", ["a.py", "b.py"]),
        ("b@x.com", ["b.py"]),
    ])
    result = GitPythonTool().run(tmp_path)
    assert result[0]["authors"] <= result[-1]["authors"]


@patch("src.tools.gitpython_tool.git.Repo", side_effect=Exception("not a repo"))
def test_run_exception_returns_empty(mock_repo_cls, tmp_path):
    assert GitPythonTool().run(tmp_path) == []


def test_not_renderable():
    assert GitPythonTool().renderable is False
