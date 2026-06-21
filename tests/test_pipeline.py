import pytest

from src.pipeline import AnalysisResult, run


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

    def test_result_git_starts_empty(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert result.git == {}

    def test_result_errors_starts_empty(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert result.errors == []
