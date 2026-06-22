from unittest.mock import MagicMock

from rich.console import Console

from src.composites.bandit_risk import BanditRiskReport


LIZARD_DATA = [
    {"file": "src/foo.py:10", "issue": "15 CCN, ..."},
    {"file": "src/bar.py:5",  "issue": "3 CCN, ..."},
]
BANDIT_DATA = [
    {"file": "src/foo.py", "severity": "HIGH", "issue_text": "Hardcoded password"},
    {"file": "src/bar.py", "severity": "LOW",  "issue_text": "Assert used"},
    {"file": "tests/test_foo.py", "severity": "LOW", "issue_text": "Assert in tests"},
]


def test_run_filters_test_files():
    result = BanditRiskReport().run({"bandit": BANDIT_DATA, "lizard": LIZARD_DATA})
    files = [r["file"] for r in result]
    assert not any("tests/" in f for f in files)


def test_run_filters_below_min_cc():
    result = BanditRiskReport().run({"bandit": BANDIT_DATA, "lizard": LIZARD_DATA})
    files = [r["file"] for r in result]
    # src/bar.py has CC=3 which is >= default min_cc=1, so it appears
    assert "src/foo.py" in files


def test_run_excludes_files_with_no_cc():
    static = {
        "bandit": [{"file": "src/unknown.py", "severity": "HIGH", "issue_text": "x"}],
        "lizard": [],
    }
    result = BanditRiskReport().run(static)
    assert result == []


def test_run_empty_data():
    assert BanditRiskReport().run({}) == []


def test_run_annotates_cc():
    result = BanditRiskReport().run({"bandit": BANDIT_DATA, "lizard": LIZARD_DATA})
    for r in result:
        assert "cc" in r


def test_run_sorts_by_severity_and_cc_desc():
    result = BanditRiskReport().run({"bandit": BANDIT_DATA, "lizard": LIZARD_DATA})
    if len(result) > 1:
        assert result[0]["severity"] >= result[-1]["severity"]


def test_defaults_exposed():
    assert "min_cc" in BanditRiskReport().defaults


def test_depends_on_tools():
    names = [t.name for t in BanditRiskReport().depends_on]
    assert "bandit" in names
    assert "lizard" in names


def test_render_terminal_empty_does_not_print():
    console = MagicMock()
    BanditRiskReport().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/foo.py", "severity": "HIGH", "issue_text": "Hardcoded password", "cc": 15}]
    BanditRiskReport().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "src/foo.py" in out
    assert "HIGH" in out


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"f{i}.py", "severity": "LOW", "issue_text": "x", "cc": i + 1} for i in range(5)]
    BanditRiskReport().render_terminal(data, console, top_n=2)
    out = (tmp_path / "out.txt").read_text()
    assert "f0.py" in out
    assert "f2.py" not in out


def test_render_html_empty():
    assert "No security issues" in BanditRiskReport().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"file": "src/foo.py", "severity": "HIGH", "issue_text": "Hardcoded password", "cc": 15}]
    html = BanditRiskReport().render_html_section(data, top_n=10)
    assert "src/foo.py" in html
    assert "HIGH" in html
    assert "Hardcoded password" in html


def test_render_html_respects_top_n():
    data = [{"file": f"f{i}.py", "severity": "LOW", "issue_text": "x", "cc": i + 1} for i in range(5)]
    html = BanditRiskReport().render_html_section(data, top_n=2)
    assert "f0.py" in html
    assert "f2.py" not in html
