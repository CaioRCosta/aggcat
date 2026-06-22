import pytest

from src.pipeline import AnalysisResult, run, _detect_github_slug


class TestDetectGithubSlug:
    def test_ssh_url(self, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text(
            '[remote "origin"]\n\turl = git@github.com:owner/repo.git\n'
        )
        assert _detect_github_slug(tmp_path) == "owner/repo"

    def test_https_url(self, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text(
            '[remote "origin"]\n\turl = https://github.com/owner/repo.git\n'
        )
        assert _detect_github_slug(tmp_path) == "owner/repo"

    def test_https_url_without_dot_git_suffix(self, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text(
            '[remote "origin"]\n\turl = https://github.com/owner/repo\n'
        )
        assert _detect_github_slug(tmp_path) == "owner/repo"

    def test_non_github_remote_returns_none(self, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text(
            '[remote "origin"]\n\turl = https://gitlab.com/owner/repo.git\n'
        )
        assert _detect_github_slug(tmp_path) is None

    def test_no_remote_origin_returns_none(self, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("[core]\n\trepositoryformatversion = 0\n")
        assert _detect_github_slug(tmp_path) is None

    def test_missing_git_config_returns_none(self, tmp_path):
        assert _detect_github_slug(tmp_path) is None

    def test_slug_stored_on_result(self, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text(
            '[remote "origin"]\n\turl = git@github.com:owner/repo.git\n'
        )
        result = run(str(tmp_path))
        assert result.github_slug == "owner/repo"

    def test_no_remote_slug_is_none_on_result(self, tmp_path):
        (tmp_path / ".git").mkdir()
        result = run(str(tmp_path))
        assert result.github_slug is None


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
