import json
from unittest.mock import patch, MagicMock

from rich.console import Console

from src.tools.cloc_tool import ClocTool


@patch("subprocess.run")
def test_run_parses_json(mock_run, tmp_path):
    fake = json.dumps({
        "header": {},
        "SUM": {},
        "src/foo.py": {"code": 100, "comment": 20, "blank": 5},
    })
    mock_run.return_value = MagicMock(stdout=fake)

    result = ClocTool().run(tmp_path)

    assert len(result) == 1
    assert result[0]["file"] == "src/foo.py"
    assert result[0]["code_lines"] == 100
    assert result[0]["comment_lines"] == 20
    assert result[0]["comment_ratio"] == 0.17


@patch("subprocess.run")
def test_run_empty_output(mock_run, tmp_path):
    mock_run.return_value = MagicMock(stdout="")
    assert ClocTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_invalid_json(mock_run, tmp_path):
    mock_run.return_value = MagicMock(stdout="not json")
    assert ClocTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_skips_header_and_sum(mock_run, tmp_path):
    fake = json.dumps({"header": {}, "SUM": {}, "a.py": {"code": 10, "comment": 0, "blank": 0}})
    mock_run.return_value = MagicMock(stdout=fake)
    result = ClocTool().run(tmp_path)
    assert all(r["file"] not in ("header", "SUM") for r in result)


@patch("subprocess.run")
def test_run_sorts_by_code_lines_descending(mock_run, tmp_path):
    fake = json.dumps({
        "a.py": {"code": 10, "comment": 0, "blank": 0},
        "b.py": {"code": 50, "comment": 0, "blank": 0},
    })
    mock_run.return_value = MagicMock(stdout=fake)
    result = ClocTool().run(tmp_path)
    assert result[0]["code_lines"] >= result[1]["code_lines"]


@patch("subprocess.run")
def test_run_zero_total_lines_ratio(mock_run, tmp_path):
    fake = json.dumps({"a.py": {"code": 0, "comment": 0, "blank": 0}})
    mock_run.return_value = MagicMock(stdout=fake)
    result = ClocTool().run(tmp_path)
    assert result[0]["comment_ratio"] == 0.0


def test_render_terminal_empty_does_not_print():
    console = MagicMock()
    ClocTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/foo.py", "code_lines": 100, "comment_lines": 20, "comment_ratio": 0.17}]
    ClocTool().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "src/foo.py" in out
    assert "100" in out


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"f{i}.py", "code_lines": i, "comment_lines": 0, "comment_ratio": 0.0} for i in range(5)]
    ClocTool().render_terminal(data, console, top_n=2)
    out = (tmp_path / "out.txt").read_text()
    assert "f0.py" in out
    assert "f2.py" not in out


def test_render_html_empty():
    assert "No data." in ClocTool().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"file": "src/foo.py", "code_lines": 100, "comment_lines": 20, "comment_ratio": 0.17}]
    html = ClocTool().render_html_section(data, top_n=10)
    assert "src/foo.py" in html
    assert "100" in html


def test_render_html_respects_top_n():
    data = [{"file": f"f{i}.py", "code_lines": i, "comment_lines": 0, "comment_ratio": 0.0} for i in range(5)]
    html = ClocTool().render_html_section(data, top_n=2)
    assert "f0.py" in html
    assert "f2.py" not in html
