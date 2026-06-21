import json
from unittest.mock import patch

import pytest
from rich.console import Console

from src.pipeline import AnalysisResult
from src.report import (
    DEFAULT_TOP_N,
    _severity_color,
    _top,
    _build_html,
    render_terminal,
    render_json,
    render_html,
)


# Fixtures


@pytest.fixture
def empty_result():
    return AnalysisResult(repo_path="/fake/repo")


@pytest.fixture
def full_result():
    return AnalysisResult(
        repo_path="/fake/repo",
        static={
            "maintainability": [
                {"file": "src/a.py", "mi": 85.0},
                {"file": "src/b.py", "mi": 55.0},
                {"file": "src/c.py", "mi": 30.0},
            ],
            "security": [
                {"file": "src/a.py", "severity": "HIGH", "issue": "hardcoded password"},
                {"file": "src/b.py", "severity": "LOW", "issue": "use of assert"},
            ],
        },
        git={
            "hotspots": [
                {"file": "src/a.py", "churn": 42, "complexity": 18},
                {"file": "src/b.py", "churn": 31, "complexity": 14},
            ],
            "truck_factor": [
                {"file": "src/a.py", "authors": 1, "commits": 87},
                {"file": "src/b.py", "authors": 3, "commits": 20},
            ],
        },
    )


# Helper tests


class TestSeverityColor:
    def test_returns_green_below_low_threshold(self):
        assert _severity_color(5, 10, 20) == "green"

    def test_returns_yellow_between_thresholds(self):
        assert _severity_color(15, 10, 20) == "yellow"

    def test_returns_red_above_high_threshold(self):
        assert _severity_color(25, 10, 20) == "red"

    def test_returns_green_at_low_threshold(self):
        assert _severity_color(10, 10, 20) == "green"

    def test_returns_yellow_at_high_threshold(self):
        assert _severity_color(20, 10, 20) == "yellow"


class TestTop:
    def test_returns_all_when_n_is_none(self):
        items = [1, 2, 3, 4, 5]
        assert _top(items, None) == items

    def test_returns_first_n_items(self):
        items = [1, 2, 3, 4, 5]
        assert _top(items, 3) == [1, 2, 3]

    def test_returns_all_when_n_exceeds_length(self):
        items = [1, 2, 3]
        assert _top(items, 10) == [1, 2, 3]

    def test_returns_empty_for_empty_list(self):
        assert _top([], 5) == []


# HTML builder tests


class TestBuildHtml:
    def test_returns_string(self, full_result):
        html = _build_html(full_result, top_n=10)
        assert isinstance(html, str)

    def test_contains_repo_path(self, full_result):
        html = _build_html(full_result, top_n=10)
        assert full_result.repo_path in html

    def test_contains_hotspot_file(self, full_result):
        html = _build_html(full_result, top_n=10)
        assert "src/a.py" in html

    def test_contains_top_note_when_top_n_set(self, full_result):
        html = _build_html(full_result, top_n=5)
        assert "Showing top 5 results" in html

    def test_no_top_note_when_all(self, full_result):
        html = _build_html(full_result, top_n=None)
        assert "Showing top" not in html

    def test_respects_top_n_limit(self, full_result):
        # full_result has 2 hotspots; with top_n=1 only first should appear
        html = _build_html(full_result, top_n=1)
        assert "src/a.py" in html
        assert "src/b.py" not in html.split("Hotspots")[1].split("Truck")[0]

    def test_is_valid_html_structure(self, full_result):
        html = _build_html(full_result, top_n=10)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html


# render_terminal tests


class TestRenderTerminal:
    def test_renders_without_error_empty(self, empty_result):
        """render_terminal should not raise even with no data."""
        render_terminal(empty_result, top_n=10)

    def test_renders_without_error_full(self, full_result):
        render_terminal(full_result, top_n=10)

    def test_renders_all_with_none_top_n(self, full_result):
        render_terminal(full_result, top_n=None)


# render_json tests


class TestRenderJson:
    def test_prints_valid_json(self, full_result, capsys):
        with patch("src.report.console") as mock_console:
            printed = []
            mock_console.print.side_effect = lambda x: printed.append(x)
            mock_console.input.return_value = "n"
            render_json(full_result, top_n=10)
        # At least one call should be the JSON string
        json_output = printed[0]
        parsed = json.loads(json_output)
        assert parsed["repo"] == full_result.repo_path

    def test_json_contains_static_and_git(self, full_result):
        with patch("src.report.console") as mock_console:
            printed = []
            mock_console.print.side_effect = lambda x: printed.append(x)
            mock_console.input.return_value = "n"
            render_json(full_result, top_n=10)
        parsed = json.loads(printed[0])
        assert "static" in parsed
        assert "git" in parsed


# render_html tests


class TestRenderHtml:
    def test_renders_without_error(self, full_result):
        with patch("src.report.console") as mock_console:
            mock_console.print.return_value = None
            mock_console.input.return_value = "n"
            render_html(full_result, top_n=10)

    def test_save_creates_file(self, full_result, tmp_path):
        output_file = tmp_path / "report.html"
        with patch("src.report.console") as mock_console:
            mock_console.print.return_value = None
            mock_console.input.side_effect = ["y", str(output_file)]
            render_html(full_result, top_n=10)
        assert output_file.exists()
        assert "aggcat" in output_file.read_text()