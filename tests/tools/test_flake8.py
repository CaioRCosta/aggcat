from unittest.mock import patch, MagicMock

from rich.console import Console

from src.tools.flake8_tool import Flake8Tool


@patch("subprocess.run")
def test_run_flake8_parses_text(mock_run, tmp_path):
    fake_flake8_output = "src/app.py:10:5: E302 expected 2 blank lines, found 1\nsrc/utils.py:42:1: W293 blank line contains whitespace"
    mock_result = MagicMock()
    mock_result.stdout = fake_flake8_output
    mock_run.return_value = mock_result

    result = Flake8Tool().run(tmp_path)

    assert len(result) == 2
    assert result[0]["file"] == "src/app.py"
    assert "E302 expected 2 blank lines" in result[0]["issue"]
    assert result[1]["file"] == "src/utils.py"


@patch("subprocess.run")
def test_run_flake8_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    result = Flake8Tool().run(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_flake8_skips_malformed_lines(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = "not a valid line\nsrc/a.py:1:1: E501 line too long"
    mock_run.return_value = mock_result

    result = Flake8Tool().run(tmp_path)
    assert len(result) == 1
    assert result[0]["file"] == "src/a.py"


@patch("subprocess.run")
def test_run_flake8_invalid_subprocess_returns_empty(mock_run, tmp_path):
    mock_run.side_effect = Exception("subprocess failed")

    result = Flake8Tool().run(tmp_path)
    assert result == []


def test_render_terminal_empty_data_does_not_print():
    console = MagicMock()
    Flake8Tool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_issues(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/app.py", "issue": "E302 expected 2 blank lines"}]
    Flake8Tool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "src/app.py" in output
    assert "E302" in output


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"src/{i}.py", "issue": "E501 line too long"} for i in range(5)]
    Flake8Tool().render_terminal(data, console, top_n=2)
    output = (tmp_path / "out.txt").read_text()
    assert "src/0.py" in output
    assert "src/2.py" not in output


def test_render_html_empty_returns_no_data():
    html = Flake8Tool().render_html_section([], top_n=10)
    assert "No data." in html


def test_render_html_contains_file():
    data = [{"file": "src/app.py", "issue": "E302 expected 2 blank lines"}]
    html = Flake8Tool().render_html_section(data, top_n=10)
    assert "src/app.py" in html


def test_render_html_respects_top_n():
    data = [{"file": f"src/{i}.py", "issue": "E501"} for i in range(5)]
    html = Flake8Tool().render_html_section(data, top_n=2)
    assert "src/0.py" in html
    assert "src/2.py" not in html
