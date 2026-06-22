from unittest.mock import MagicMock

from rich.console import Console

from src.composites.hotspots import HotspotsReport


LIZARD_DATA = [
    {"file": "src/foo.py:10", "issue": "15 CCN, ..."},
    {"file": "src/bar.py:5",  "issue": "3 CCN, ..."},
]
PYDRILLER_DATA = [
    {"file": "src/foo.py", "churn": 10},
    {"file": "src/bar.py", "churn": 10},
]


def test_run_returns_hotspots_above_threshold():
    report = HotspotsReport()
    static = {"pydriller": PYDRILLER_DATA, "lizard": LIZARD_DATA}
    result = report.run(static)
    files = [r["file"] for r in result]
    assert "src/foo.py" in files
    assert "src/bar.py" not in files  # CC=3 < default min_cc=10


def test_run_empty_data():
    assert HotspotsReport().run({}) == []


def test_run_churn_below_threshold():
    report = HotspotsReport()
    static = {
        "pydriller": [{"file": "src/foo.py", "churn": 1}],
        "lizard": [{"file": "src/foo.py:1", "issue": "15 CCN, ..."}],
    }
    assert report.run(static) == []


def test_run_sorts_by_churn_descending():
    report = HotspotsReport()
    static = {
        "pydriller": [{"file": "a.py", "churn": 5}, {"file": "b.py", "churn": 20}],
        "lizard": [{"file": "a.py:1", "issue": "15 CCN,"}, {"file": "b.py:1", "issue": "15 CCN,"}],
    }
    result = report.run(static)
    assert result[0]["churn"] >= result[-1]["churn"]


def test_defaults_exposed():
    d = HotspotsReport().defaults
    assert "min_churn" in d
    assert "min_cc" in d


def test_depends_on_tools():
    deps = HotspotsReport().depends_on
    names = [t.name for t in deps]
    assert "pydriller" in names
    assert "lizard" in names


def test_render_terminal_empty_does_not_print():
    console = MagicMock()
    HotspotsReport().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/foo.py", "churn": 10, "cc": 15}]
    HotspotsReport().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "src/foo.py" in out


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"f{i}.py", "churn": i, "cc": 15} for i in range(5)]
    HotspotsReport().render_terminal(data, console, top_n=2)
    out = (tmp_path / "out.txt").read_text()
    assert "f0.py" in out
    assert "f2.py" not in out


def test_render_html_empty():
    assert "No hotspots" in HotspotsReport().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"file": "src/foo.py", "churn": 10, "cc": 15}]
    html = HotspotsReport().render_html_section(data, top_n=10)
    assert "src/foo.py" in html
    assert "10" in html


def test_render_html_respects_top_n():
    data = [{"file": f"f{i}.py", "churn": i, "cc": 15} for i in range(5)]
    html = HotspotsReport().render_html_section(data, top_n=2)
    assert "f0.py" in html
    assert "f2.py" not in html
