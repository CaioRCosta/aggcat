from unittest.mock import MagicMock

from rich.console import Console

from src.composites.truck_factor import TruckFactorReport


GITPYTHON_DATA = [
    {"file": "src/foo.py", "authors": 1, "commits": 50},
    {"file": "src/bar.py", "authors": 2, "commits": 20},
    {"file": "src/baz.py", "authors": 5, "commits": 30},
]


def test_run_filters_by_max_authors():
    result = TruckFactorReport().run({"gitpython": GITPYTHON_DATA})
    files = [r["file"] for r in result]
    assert "src/foo.py" in files
    assert "src/bar.py" in files
    assert "src/baz.py" not in files


def test_run_empty_data():
    assert TruckFactorReport().run({}) == []


def test_run_sorts_by_authors_then_commits_desc():
    report = TruckFactorReport()
    data = [
        {"file": "a.py", "authors": 1, "commits": 10},
        {"file": "b.py", "authors": 1, "commits": 30},
        {"file": "c.py", "authors": 2, "commits": 5},
    ]
    result = report.run({"gitpython": data})
    assert result[0]["authors"] <= result[-1]["authors"]
    # among same authors, higher commits comes first
    same_author = [r for r in result if r["authors"] == 1]
    assert same_author[0]["commits"] >= same_author[-1]["commits"]


def test_defaults_exposed():
    assert "max_authors" in TruckFactorReport().defaults


def test_depends_on_tools():
    names = [t.name for t in TruckFactorReport().depends_on]
    assert "gitpython" in names


def test_render_terminal_empty_does_not_print():
    console = MagicMock()
    TruckFactorReport().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/foo.py", "authors": 1, "commits": 50}]
    TruckFactorReport().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "src/foo.py" in out


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"f{i}.py", "authors": 1, "commits": i} for i in range(5)]
    TruckFactorReport().render_terminal(data, console, top_n=2)
    out = (tmp_path / "out.txt").read_text()
    assert "f0.py" in out
    assert "f2.py" not in out


def test_render_html_empty():
    assert "No truck factor" in TruckFactorReport().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"file": "src/foo.py", "authors": 1, "commits": 50}]
    html = TruckFactorReport().render_html_section(data, top_n=10)
    assert "src/foo.py" in html


def test_render_html_respects_top_n():
    data = [{"file": f"f{i}.py", "authors": 1, "commits": i} for i in range(5)]
    html = TruckFactorReport().render_html_section(data, top_n=2)
    assert "f0.py" in html
    assert "f2.py" not in html
