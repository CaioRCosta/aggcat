from unittest.mock import patch, MagicMock

from rich.console import Console

from src.tools.lizard_tool import LizardTool


@patch("subprocess.run")
def test_run_lizard_parses_warnings(mock_run, tmp_path):
    fake_output = "src/math.py:50: warning: process_data has 12 CCN\nsrc/api.py:10: warning: route has 22 CCN"
    mock_result = MagicMock()
    mock_result.stdout = fake_output
    mock_run.return_value = mock_result

    result = LizardTool().run(tmp_path)

    assert len(result) == 2
    assert result[0]["file"] == "src/math.py:50"
    assert "12 CCN" in result[0]["issue"]


@patch("subprocess.run")
def test_run_lizard_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    result = LizardTool().run(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_lizard_ignores_lines_without_warning(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = "some info line\nsrc/a.py:5: warning: func has 15 CCN"
    mock_run.return_value = mock_result

    result = LizardTool().run(tmp_path)
    assert len(result) == 1
    assert result[0]["file"] == "src/a.py:5"


@patch("subprocess.run")
def test_run_lizard_passes_cc_threshold(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    LizardTool().run(tmp_path)

    cmd = mock_run.call_args[0][0]
    assert "-C" in cmd


@patch("subprocess.run")
def test_run_lizard_invalid_subprocess_returns_empty(mock_run, tmp_path):
    mock_run.side_effect = Exception("subprocess failed")

    result = LizardTool().run(tmp_path)
    assert result == []


def test_render_terminal_empty_data_does_not_print():
    console = MagicMock()
    LizardTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_issues(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/math.py:50", "issue": "process_data has 12 CCN"}]
    LizardTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "src/math.py:50" in output
    assert "12 CCN" in output


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"src/{i}.py:1", "issue": "has 15 CCN"} for i in range(5)]
    LizardTool().render_terminal(data, console, top_n=2)
    output = (tmp_path / "out.txt").read_text()
    assert "src/0.py:1" in output
    assert "src/2.py:1" not in output


def test_render_html_empty_returns_no_data():
    html = LizardTool().render_html_section([], top_n=10)
    assert "No data." in html


def test_render_html_contains_file():
    data = [{"file": "src/math.py:50", "issue": "process_data has 12 CCN"}]
    html = LizardTool().render_html_section(data, top_n=10)
    assert "src/math.py:50" in html


def test_render_html_respects_top_n():
    data = [{"file": f"src/{i}.py:1", "issue": "high CCN"} for i in range(5)]
    html = LizardTool().render_html_section(data, top_n=2)
    assert "src/0.py:1" in html
    assert "src/2.py:1" not in html
