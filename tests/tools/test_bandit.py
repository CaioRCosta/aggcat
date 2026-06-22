import json
from unittest.mock import patch, MagicMock

from rich.console import Console

from src.tools.bandit_tool import BanditTool


@patch("subprocess.run")
def test_run_bandit_parses_json(mock_run, tmp_path):
    fake_bandit_output = json.dumps({
        "results": [
            {
                "filename": "auth.py",
                "issue_severity": "HIGH",
                "issue_text": "Hardcoded password"
            }
        ]
    })
    mock_result = MagicMock()
    mock_result.stdout = fake_bandit_output
    mock_run.return_value = mock_result

    result = BanditTool().run(tmp_path)

    assert len(result) == 1
    assert result[0]["severity"] == "HIGH"
    assert "Hardcoded" in result[0]["issue_text"]


@patch("subprocess.run")
def test_run_bandit_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    result = BanditTool().run(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_bandit_sorts_by_severity(mock_run, tmp_path):
    fake_output = json.dumps({
        "results": [
            {"filename": "a.py", "issue_severity": "LOW", "issue_text": "low issue"},
            {"filename": "b.py", "issue_severity": "HIGH", "issue_text": "high issue"},
            {"filename": "c.py", "issue_severity": "MEDIUM", "issue_text": "medium issue"},
        ]
    })
    mock_result = MagicMock()
    mock_result.stdout = fake_output
    mock_run.return_value = mock_result

    result = BanditTool().run(tmp_path)

    assert [r["severity"] for r in result] == ["HIGH", "MEDIUM", "LOW"]


@patch("subprocess.run")
def test_run_bandit_invalid_json_returns_empty(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = "not valid json"
    mock_run.return_value = mock_result

    result = BanditTool().run(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_bandit_excludes_existing_venv(mock_run, tmp_path):
    (tmp_path / "venv").mkdir()
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    BanditTool().run(tmp_path)

    cmd = mock_run.call_args[0][0]
    assert "--exclude" in cmd
    exclude_val = cmd[cmd.index("--exclude") + 1]
    assert any(p.endswith("/venv") for p in exclude_val.split(","))


@patch("subprocess.run")
def test_run_bandit_always_excludes_tests_dir(mock_run, tmp_path):
    (tmp_path / "tests").mkdir()
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    BanditTool().run(tmp_path)

    cmd = mock_run.call_args[0][0]
    assert "--exclude" in cmd
    exclude_val = cmd[cmd.index("--exclude") + 1]
    assert any(p.endswith("/tests") for p in exclude_val.split(","))


def test_render_terminal_empty_data_does_not_print():
    console = MagicMock()
    BanditTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_issues(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "auth.py", "severity": "HIGH", "issue_text": "Hardcoded password"}]
    BanditTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "auth.py" in output
    assert "HIGH" in output


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [
        {"file": f"src/{i}.py", "severity": "LOW", "issue_text": "issue"}
        for i in range(5)
    ]
    BanditTool().render_terminal(data, console, top_n=2)
    output = (tmp_path / "out.txt").read_text()
    assert "src/0.py" in output
    assert "src/2.py" not in output


def test_render_html_empty_returns_no_data():
    html = BanditTool().render_html_section([], top_n=10)
    assert "No data." in html


def test_render_html_contains_file_and_severity():
    data = [{"file": "auth.py", "severity": "HIGH", "issue_text": "Hardcoded password"}]
    html = BanditTool().render_html_section(data, top_n=10)
    assert "auth.py" in html
    assert "HIGH" in html


def test_render_html_respects_top_n():
    data = [{"file": f"src/{i}.py", "severity": "LOW", "issue_text": "x"} for i in range(5)]
    html = BanditTool().render_html_section(data, top_n=2)
    assert "src/0.py" in html
    assert "src/2.py" not in html
