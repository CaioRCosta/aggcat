from unittest.mock import patch, MagicMock

from rich.console import Console

from src.tools.vulture_tool import VultureTool


@patch("subprocess.run")
def test_run_vulture_parses_text(mock_run, tmp_path):
    fake_vulture_output = "src/utils.py:15: unused function 'helper' (60%)\nsrc/main.py:42: unused import 'os' (100%)"
    mock_result = MagicMock()
    mock_result.stdout = fake_vulture_output
    mock_run.return_value = mock_result

    result = VultureTool().run(tmp_path)

    assert len(result) == 2
    assert result[0]["file"] == "src/utils.py"
    assert "unused function 'helper'" in result[0]["issue"]
    assert result[1]["file"] == "src/main.py"


@patch("subprocess.run")
def test_run_vulture_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    result = VultureTool().run(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_vulture_skips_malformed_lines(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = "no colon here\nsrc/a.py:10: unused variable 'x' (80%)"
    mock_run.return_value = mock_result

    result = VultureTool().run(tmp_path)
    assert len(result) == 1
    assert result[0]["file"] == "src/a.py"


@patch("subprocess.run")
def test_run_vulture_passes_min_confidence(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    VultureTool().run(tmp_path)

    cmd = mock_run.call_args[0][0]
    assert "--min-confidence" in cmd


def test_render_terminal_empty_data_does_not_print():
    console = MagicMock()
    VultureTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_issues(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/utils.py", "issue": "unused function 'helper'"}]
    VultureTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "src/utils.py" in output
    assert "unused function" in output


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"src/{i}.py", "issue": "unused"} for i in range(5)]
    VultureTool().render_terminal(data, console, top_n=2)
    output = (tmp_path / "out.txt").read_text()
    assert "src/0.py" in output
    assert "src/2.py" not in output


def test_render_html_empty_returns_no_data():
    html = VultureTool().render_html_section([], top_n=10)
    assert "No data." in html


def test_render_html_contains_file():
    data = [{"file": "src/utils.py", "issue": "unused function 'helper'"}]
    html = VultureTool().render_html_section(data, top_n=10)
    assert "src/utils.py" in html


def test_render_html_respects_top_n():
    data = [{"file": f"src/{i}.py", "issue": "unused"} for i in range(5)]
    html = VultureTool().render_html_section(data, top_n=2)
    assert "src/0.py" in html
    assert "src/2.py" not in html
