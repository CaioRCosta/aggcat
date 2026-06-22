import json
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

from src.tools.radon_tool import RadonTool

@patch("subprocess.run")
def test_run_radon_parses_json(mock_run, tmp_path):
    fake_radon_output = json.dumps({
        "src/app.py": {"mi": 45.33333, "rank": "C"}
    })
    
    mock_result = MagicMock()
    mock_result.stdout = fake_radon_output
    mock_run.return_value = mock_result
    
    result = RadonTool().run(tmp_path)
    
    assert len(result) == 1
    assert result[0]["file"] == "src/app.py"
    assert result[0]["mi"] == 45.33


@patch("subprocess.run")
def test_run_radon_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = " "
    mock_run.return_value = mock_result

    result = RadonTool().run(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_radon_sorts_by_mi_ascending(mock_run, tmp_path):
    fake_output = json.dumps({
        "src/a.py": {"mi": 90.0},
        "src/b.py": {"mi": 20.0},
        "src/c.py": {"mi": 55.0},
    })
    mock_result = MagicMock()
    mock_result.stdout = fake_output
    mock_run.return_value = mock_result

    result = RadonTool().run(tmp_path)
    assert [r["mi"] for r in result] == [20.0, 55.0, 90.0]


@patch("subprocess.run")
def test_run_radon_invalid_json_returns_empty(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = "not valid json"
    mock_run.return_value = mock_result

    result = RadonTool().run(tmp_path)
    assert result == []


def test_render_terminal_empty_data_does_not_print():
    console = MagicMock()
    RadonTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_grade_a(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/a.py", "mi": 85.0}]
    RadonTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "src/a.py" in output
    assert "A" in output


def test_render_terminal_grade_b(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/b.py", "mi": 65.0}]
    RadonTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "B" in output


def test_render_terminal_grade_c(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/c.py", "mi": 45.0}]
    RadonTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "C" in output


def test_render_terminal_grade_d(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/d.py", "mi": 20.0}]
    RadonTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "D" in output


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"src/{i}.py", "mi": float(i * 10)} for i in range(1, 6)]
    RadonTool().render_terminal(data, console, top_n=2)
    output = (tmp_path / "out.txt").read_text()
    assert "src/1.py" in output
    assert "src/3.py" not in output


def test_render_html_empty_returns_no_data():
    html = RadonTool().render_html_section([], top_n=10)
    assert "No data." in html


def test_render_html_contains_file():
    data = [{"file": "src/a.py", "mi": 85.0}]
    html = RadonTool().render_html_section(data, top_n=10)
    assert "src/a.py" in html


def test_render_html_respects_top_n():
    data = [{"file": f"src/{i}.py", "mi": float(i * 10)} for i in range(1, 6)]
    html = RadonTool().render_html_section(data, top_n=2)
    assert "src/1.py" in html
    assert "src/3.py" not in html
