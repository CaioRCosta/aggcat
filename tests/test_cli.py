from io import StringIO
from unittest.mock import patch, MagicMock

import pytest
import typer
from typer.testing import CliRunner

import src.cli as cli_module
from src.analyzer import TOOLS
from src.cli import app
from src.pipeline import AnalysisResult

runner = CliRunner()

_FAKE_RESULT = AnalysisResult(repo_path="/fake/repo")


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
    @pytest.fixture(autouse=True)
    def mock_pipeline(self):
        with patch("src.cli.pipeline.run", return_value=_FAKE_RESULT):
            yield

    def test_analyze_requires_repo_argument(self):
        result = runner.invoke(app, ["analyze"])
        assert result.exit_code != 0

    def test_analyze_prints_repo_path(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(app, ["analyze", str(tmp_path)])
        assert result.exit_code == 0
        assert _FAKE_RESULT.repo_path in result.output

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


@pytest.mark.xdist_group("config")
class TestCLIConfig:
    @pytest.fixture(autouse=True)
    def reset_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        yield
        runner.invoke(app, ["config", "reset"])

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

    def test_config_set_float_value(self):
        result = runner.invoke(app, ["config", "set", "radon", "mi_grade_a", "65.5"])
        assert result.exit_code == 0
        show_result = runner.invoke(app, ["config", "show"])
        assert "mi_grade_a = 65.5" in show_result.output

    def test_config_set_invalid_value_type_fails(self):
        result = runner.invoke(app, ["config", "set", "lizard", "cc_low", "notanumber"])
        assert result.exit_code != 0
        assert "could not be cast" in result.output

    def test_config_set_invalid_tool_fails(self):
        result = runner.invoke(app, ["config", "set", "nonexistent_tool", "cc_low", "15"])
        assert result.exit_code != 0
        assert "not configurable" in result.output

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


class TestGetChar:
    def test_fallback_when_not_tty(self):
        with patch.object(cli_module, "tty", None), \
             patch("sys.stdin", StringIO("x")):
            assert cli_module.get_char() == "x"

    def test_fallback_when_stdin_not_tty(self):
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "a"
        with patch("sys.stdin", mock_stdin):
            assert cli_module.get_char() == "a"

    def test_tty_reads_regular_char(self):
        mock_tty = MagicMock()
        mock_termios = MagicMock()
        mock_termios.tcgetattr.return_value = []
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        mock_stdin.fileno.return_value = 0
        mock_stdin.read.return_value = "z"
        with patch.object(cli_module, "tty", mock_tty), \
             patch.object(cli_module, "termios", mock_termios), \
             patch("sys.stdin", mock_stdin):
            assert cli_module.get_char() == "z"

    def test_tty_reads_escape_sequence(self):
        mock_tty = MagicMock()
        mock_termios = MagicMock()
        mock_termios.tcgetattr.return_value = []
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        mock_stdin.fileno.return_value = 0
        mock_stdin.read.side_effect = ["\x1b", "[A"]
        with patch.object(cli_module, "tty", mock_tty), \
             patch.object(cli_module, "termios", mock_termios), \
             patch("sys.stdin", mock_stdin):
            assert cli_module.get_char() == "\x1b[A"


class TestSelectToolsInteractive:
    @pytest.fixture(autouse=True)
    def tty_active(self):
        with patch("sys.stdin") as mock_stdin, \
             patch("sys.stdout"):
            mock_stdin.isatty.return_value = True
            self.mock_stdin = mock_stdin
            yield

    def _run(self, keys):
        with patch.object(cli_module, "get_char", side_effect=keys):
            return cli_module.select_tools_interactive()

    def test_enter_returns_all_tools(self):
        result = self._run(["\r"])
        assert result == TOOLS

    def test_space_deselects_first_tool(self):
        result = self._run([" ", "\r"])
        assert TOOLS[0] not in result
        assert len(result) == len(TOOLS) - 1

    def test_down_then_enter_returns_all(self):
        result = self._run(["\x1b[B", "\r"])
        assert result == TOOLS

    def test_up_wraps_to_last_tool(self):
        result = self._run(["\x1b[A", " ", "\r"])
        assert TOOLS[-1] not in result

    def test_deselect_all_raises_exit(self):
        # Space deselects current, Down moves to next — repeat for all tools
        keys = ([" ", "\x1b[B"] * len(TOOLS))[:-1] + ["\r"]
        with pytest.raises(typer.Exit):
            self._run(keys)

    def test_ctrl_c_calls_sys_exit(self):
        with pytest.raises(SystemExit):
            self._run(["\x03"])
