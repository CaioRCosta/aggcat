"""Unit tests for aggcat CLI and pipeline (Pessoa 1 — infrastructure)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from aggcat.cli import app
from aggcat.pipeline import AnalysisResult, run

runner = CliRunner()


# ── CLI tests ────────────────────────────────────────────────────────────────


class TestCLIHelp:
    def test_help_exits_zero(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_help_contains_analyze(self):
        result = runner.invoke(app, ["--help"])
        assert "analyze" in result.output

    def test_version_command(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "aggcat" in result.output


class TestCLIAnalyze:
    def test_analyze_requires_repo_argument(self):
        result = runner.invoke(app, ["analyze"])
        assert result.exit_code != 0

    def test_analyze_prints_repo_path(self, tmp_path):
        # Create a minimal git repo so the path exists
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path)])
        assert result.exit_code == 0
        assert str(tmp_path) in result.output

    def test_analyze_default_output_is_terminal(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path)])
        assert result.exit_code == 0
        assert "aggcat report" in result.output

    def test_analyze_accepts_json_output(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path), "--output", "json"], input="n\n")
        assert result.exit_code == 0

    def test_analyze_accepts_github_repo_flag(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(
            app, ["analyze", str(tmp_path), "--github-repo", "owner/repo"]
        )
        assert result.exit_code == 0
        assert "aggcat report" in result.output


# ── Pipeline tests ────────────────────────────────────────────────────────────


class TestPipeline:
    def test_run_returns_analysis_result(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert isinstance(result, AnalysisResult)

    def test_run_stores_repo_path(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert result.repo_path == str(tmp_path.resolve())

    def test_run_raises_on_missing_path(self):
        with pytest.raises(FileNotFoundError):
            run("/this/path/does/not/exist")

    def test_result_static_starts_empty(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert result.static == {}

    def test_result_git_starts_empty(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert result.git == {}

    def test_result_errors_starts_empty(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert result.errors == []