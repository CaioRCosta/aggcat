import json
from unittest.mock import patch, MagicMock

from src.tools.coverage_tool import CoverageTool


def test_run_returns_empty_when_no_coverage_file(tmp_path):
    assert CoverageTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_parses_coverage_json(mock_run, tmp_path):
    (tmp_path / ".coverage").touch()
    fake = json.dumps({
        "files": {
            "src/foo.py": {"summary": {"covered_lines": 80, "num_statements": 100}},
        }
    })
    mock_run.return_value = MagicMock(stdout=fake)

    result = CoverageTool().run(tmp_path)

    assert len(result) == 1
    assert result[0]["file"] == "src/foo.py"
    assert result[0]["coverage_pct"] == 80.0
    assert result[0]["covered_lines"] == 80
    assert result[0]["total_lines"] == 100


@patch("subprocess.run")
def test_run_empty_output(mock_run, tmp_path):
    (tmp_path / ".coverage").touch()
    mock_run.return_value = MagicMock(stdout="")
    assert CoverageTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_invalid_json(mock_run, tmp_path):
    (tmp_path / ".coverage").touch()
    mock_run.return_value = MagicMock(stdout="bad json")
    assert CoverageTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_zero_statements_defaults_to_100(mock_run, tmp_path):
    (tmp_path / ".coverage").touch()
    fake = json.dumps({"files": {"a.py": {"summary": {"covered_lines": 0, "num_statements": 0}}}})
    mock_run.return_value = MagicMock(stdout=fake)
    result = CoverageTool().run(tmp_path)
    assert result[0]["coverage_pct"] == 100.0


@patch("subprocess.run")
def test_run_sorts_by_coverage_ascending(mock_run, tmp_path):
    (tmp_path / ".coverage").touch()
    fake = json.dumps({"files": {
        "a.py": {"summary": {"covered_lines": 90, "num_statements": 100}},
        "b.py": {"summary": {"covered_lines": 10, "num_statements": 100}},
    }})
    mock_run.return_value = MagicMock(stdout=fake)
    result = CoverageTool().run(tmp_path)
    assert result[0]["coverage_pct"] <= result[1]["coverage_pct"]


def test_not_renderable():
    assert CoverageTool().renderable is False
