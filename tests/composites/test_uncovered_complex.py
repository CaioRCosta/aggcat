from unittest.mock import MagicMock

from rich.console import Console

from src.composites.uncovered_complex import UncoveredComplexReport


LIZARD_DATA = [
    {"file": "src/foo.py:10", "issue": "15 CCN, ..."},
    {"file": "src/bar.py:5",  "issue": "3 CCN, ..."},
]
COVERAGE_DATA = [
    {"file": "src/foo.py", "coverage_pct": 40.0},
    {"file": "src/bar.py", "coverage_pct": 40.0},
]


def test_run_returns_uncovered_complex():
    report = UncoveredComplexReport()
    static = {"lizard": LIZARD_DATA, "coverage": COVERAGE_DATA}
    result = report.run(static)
    files = [r["file"] for r in result]
    assert "src/foo.py" in files
    assert "src/bar.py" not in files  # CC=3 < default min_cc=10


def test_run_excludes_well_covered_files():
    report = UncoveredComplexReport()
    static = {
        "lizard": [{"file": "src/foo.py:1", "issue": "15 CCN,"}],
        "coverage": [{"file": "src/foo.py", "coverage_pct": 90.0}],
    }
    assert report.run(static) == []


def test_run_skips_files_without_coverage():
    report = UncoveredComplexReport()
    static = {
        "lizard": [{"file": "src/foo.py:1", "issue": "15 CCN,"}],
        "coverage": [],
    }
    assert report.run(static) == []


def test_run_empty_data():
    assert UncoveredComplexReport().run({}) == []


def test_run_sorts_by_cc_descending():
    report = UncoveredComplexReport()
    static = {
        "lizard": [
            {"file": "a.py:1", "issue": "20 CCN,"},
            {"file": "b.py:1", "issue": "12 CCN,"},
        ],
        "coverage": [
            {"file": "a.py", "coverage_pct": 10.0},
            {"file": "b.py", "coverage_pct": 10.0},
        ],
    }
    result = report.run(static)
    assert result[0]["cc"] >= result[-1]["cc"]


def test_defaults_exposed():
    d = UncoveredComplexReport().defaults
    assert "max_coverage" in d
    assert "min_cc" in d


def test_depends_on_tools():
    names = [t.name for t in UncoveredComplexReport().depends_on]
    assert "coverage" in names
    assert "lizard" in names


def test_render_terminal_empty_does_not_print():
    console = MagicMock()
    UncoveredComplexReport().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "src/foo.py", "coverage_pct": 40.0, "cc": 15}]
    UncoveredComplexReport().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "src/foo.py" in out


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"f{i}.py", "coverage_pct": 10.0, "cc": i + 10} for i in range(5)]
    UncoveredComplexReport().render_terminal(data, console, top_n=2)
    out = (tmp_path / "out.txt").read_text()
    assert "f0.py" in out
    assert "f2.py" not in out


def test_render_html_empty():
    assert "No uncovered" in UncoveredComplexReport().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"file": "src/foo.py", "coverage_pct": 40.0, "cc": 15}]
    html = UncoveredComplexReport().render_html_section(data, top_n=10)
    assert "src/foo.py" in html
    assert "40.0%" in html


def test_render_html_respects_top_n():
    data = [{"file": f"f{i}.py", "coverage_pct": 10.0, "cc": i + 10} for i in range(5)]
    html = UncoveredComplexReport().render_html_section(data, top_n=2)
    assert "f0.py" in html
    assert "f2.py" not in html
