from __future__ import annotations

import pytest
from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


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

    def test_analyze_all_flag_exits_zero(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path), "--all"])
        assert result.exit_code == 0

    def test_analyze_all_flag_runs_without_selector(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path), "--all"])
        assert "aggcat report" in result.output

    def test_analyze_top_n_limits_results(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path), "--top-n", "5"])
        assert result.exit_code == 0
        assert "Showing top 5" in result.output

    def test_analyze_default_shows_all_results(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path), "--all"])
        assert "Showing top" not in result.output

    def test_analyze_invalid_output_exits_nonzero(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path), "--output", "pdf"])
        assert result.exit_code != 0

    def test_analyze_invalid_output_shows_error_message(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path), "--output", "pdf"])
        assert "Unknown output format" in result.output


class TestCLIConfig:
    def test_config_show_exits_zero(self):
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert "radon" in result.output

    def test_config_set_updates_value(self):
        runner.invoke(app, ["config", "reset"])
        result = runner.invoke(app, ["config", "set", "lizard", "cc_low", "15"])
        assert result.exit_code == 0
        assert "cc_low = 15" in result.output or "Config updated" in result.output

        show_result = runner.invoke(app, ["config", "show"])
        assert "cc_low = 15" in show_result.output

    def test_config_set_invalid_key_fails(self):
        result = runner.invoke(app, ["config", "set", "lizard", "non_existent_key", "15"])
        assert result.exit_code != 0
        assert "not configurable" in result.output

    def test_config_reset_restores_defaults(self):
        runner.invoke(app, ["config", "set", "lizard", "cc_low", "15"])
        reset_result = runner.invoke(app, ["config", "reset"])
        assert reset_result.exit_code == 0

        show_result = runner.invoke(app, ["config", "show"])
        assert "cc_low = 10" in show_result.output
