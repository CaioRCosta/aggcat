from unittest.mock import patch, MagicMock

from src.tools.pydriller_tool import PyDrillerTool


def _make_commit(files):
    commit = MagicMock()
    modified = []
    for path in files:
        f = MagicMock()
        f.new_path = path
        f.old_path = None
        modified.append(f)
    commit.modified_files = modified
    return commit


@patch("src.tools.pydriller_tool.Repository")
def test_run_counts_churn(mock_repo, tmp_path):
    mock_repo.return_value.traverse_commits.return_value = [
        _make_commit(["src/a.py", "src/b.py"]),
        _make_commit(["src/a.py"]),
    ]
    result = PyDrillerTool().run(tmp_path)
    by_file = {r["file"]: r["churn"] for r in result}
    assert by_file["src/a.py"] == 2
    assert by_file["src/b.py"] == 1


@patch("src.tools.pydriller_tool.Repository")
def test_run_sorts_by_churn_descending(mock_repo, tmp_path):
    mock_repo.return_value.traverse_commits.return_value = [
        _make_commit(["a.py"]),
        _make_commit(["b.py", "b.py"]),
        _make_commit(["b.py"]),
    ]
    result = PyDrillerTool().run(tmp_path)
    assert result[0]["churn"] >= result[-1]["churn"]


@patch("src.tools.pydriller_tool.Repository")
def test_run_skips_venv(mock_repo, tmp_path):
    mock_repo.return_value.traverse_commits.return_value = [
        _make_commit(["venv/lib/pkg.py", "src/clean.py"]),
    ]
    result = PyDrillerTool().run(tmp_path)
    assert all("venv" not in r["file"] for r in result)


@patch("src.tools.pydriller_tool.Repository")
def test_run_handles_none_path(mock_repo, tmp_path):
    commit = MagicMock()
    f = MagicMock()
    f.new_path = None
    f.old_path = None
    commit.modified_files = [f]
    mock_repo.return_value.traverse_commits.return_value = [commit]
    result = PyDrillerTool().run(tmp_path)
    assert result == []


@patch("src.tools.pydriller_tool.Repository", side_effect=Exception("boom"))
def test_run_exception_returns_empty(mock_repo, tmp_path):
    assert PyDrillerTool().run(tmp_path) == []


def test_not_renderable():
    assert PyDrillerTool().renderable is False
