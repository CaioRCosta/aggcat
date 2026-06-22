import json
from unittest.mock import patch, MagicMock

from rich.console import Console

from src.tools.pip_audit_tool import PipAuditTool


@patch("subprocess.run")
def test_run_parses_vulns(mock_run, tmp_path):
    fake = json.dumps({
        "dependencies": [{
            "name": "requests",
            "version": "2.0.0",
            "vulns": [{"id": "CVE-123", "description": "A bug", "fix_versions": ["2.1.0"]}],
        }]
    })
    mock_run.return_value = MagicMock(stdout=fake)

    result = PipAuditTool().run(tmp_path)

    assert len(result) == 1
    assert result[0]["package"] == "requests"
    assert result[0]["vuln_id"] == "CVE-123"
    assert result[0]["fix_versions"] == "2.1.0"


@patch("subprocess.run")
def test_run_empty_output(mock_run, tmp_path):
    mock_run.return_value = MagicMock(stdout="")
    assert PipAuditTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_invalid_json(mock_run, tmp_path):
    mock_run.return_value = MagicMock(stdout="bad json")
    assert PipAuditTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_no_vulns_returns_empty(mock_run, tmp_path):
    fake = json.dumps({"dependencies": [{"name": "requests", "version": "2.0.0", "vulns": []}]})
    mock_run.return_value = MagicMock(stdout=fake)
    assert PipAuditTool().run(tmp_path) == []


@patch("subprocess.run")
def test_run_no_fix_versions_shows_dash(mock_run, tmp_path):
    fake = json.dumps({"dependencies": [{
        "name": "pkg", "version": "1.0", "vulns": [{"id": "X", "description": "d", "fix_versions": []}]
    }]})
    mock_run.return_value = MagicMock(stdout=fake)
    result = PipAuditTool().run(tmp_path)
    assert result[0]["fix_versions"] == "—"


def test_render_terminal_empty_does_not_print():
    console = MagicMock()
    PipAuditTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"package": "requests", "version": "2.0.0", "vuln_id": "CVE-123", "description": "bug", "fix_versions": "2.1.0"}]
    PipAuditTool().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "requests" in out
    assert "CVE-123" in out


def test_render_html_empty():
    assert "No vulnerabilities" in PipAuditTool().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"package": "requests", "version": "2.0.0", "vuln_id": "CVE-123", "description": "bug", "fix_versions": "2.1.0"}]
    html = PipAuditTool().render_html_section(data, top_n=10)
    assert "requests" in html
    assert "CVE-123" in html


def test_render_html_respects_top_n():
    data = [
        {"package": f"pkg{i}", "version": "1.0", "vuln_id": f"CVE-{i}", "description": "x", "fix_versions": "—"}
        for i in range(5)
    ]
    html = PipAuditTool().render_html_section(data, top_n=2)
    assert "pkg0" in html
    assert "pkg2" not in html
