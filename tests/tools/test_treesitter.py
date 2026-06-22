from rich.console import Console

from src.tools.treesitter_tool import TreesitterTool, _AVAILABLE


def test_run_returns_empty_when_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr("src.tools.treesitter_tool._AVAILABLE", False)
    assert TreesitterTool().run(tmp_path) == []


def test_run_detects_bare_except(tmp_path):
    if not _AVAILABLE:
        return
    (tmp_path / "a.py").write_text("try:\n    pass\nexcept:\n    pass\n")
    result = TreesitterTool().run(tmp_path)
    patterns = [r["pattern"] for r in result]
    assert "bare_except" in patterns


def test_run_detects_broad_except_exception(tmp_path):
    if not _AVAILABLE:
        return
    (tmp_path / "a.py").write_text("try:\n    pass\nexcept Exception:\n    pass\n")
    result = TreesitterTool().run(tmp_path)
    patterns = [r["pattern"] for r in result]
    assert "broad_except_exception" in patterns


def test_run_skips_venv(tmp_path):
    if not _AVAILABLE:
        return
    venv = tmp_path / "venv"
    venv.mkdir()
    (venv / "a.py").write_text("try:\n    pass\nexcept:\n    pass\n")
    result = TreesitterTool().run(tmp_path)
    assert all("venv" not in r["file"] for r in result)


def test_run_clean_file_returns_empty(tmp_path):
    if not _AVAILABLE:
        return
    (tmp_path / "clean.py").write_text("x = 1\n")
    result = TreesitterTool().run(tmp_path)
    assert result == []


def test_run_result_has_expected_fields(tmp_path):
    if not _AVAILABLE:
        return
    (tmp_path / "a.py").write_text("try:\n    pass\nexcept:\n    pass\n")
    result = TreesitterTool().run(tmp_path)
    assert len(result) > 0
    for r in result:
        assert "file" in r
        assert "line" in r
        assert "pattern" in r
        assert "description" in r


def test_render_terminal_empty_does_not_print():
    from unittest.mock import MagicMock
    console = MagicMock()
    TreesitterTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "a.py", "line": 3, "pattern": "bare_except", "description": "Bare except."}]
    TreesitterTool().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "a.py" in out
    assert "bare_except" in out


def test_render_html_empty():
    assert "No anti-patterns" in TreesitterTool().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"file": "a.py", "line": 3, "pattern": "bare_except", "description": "Bare except."}]
    html = TreesitterTool().render_html_section(data, top_n=10)
    assert "bare_except" in html
    assert "a.py:3" in html


def test_render_html_respects_top_n():
    data = [{"file": f"f{i}.py", "line": i, "pattern": "bare_except", "description": "x"} for i in range(5)]
    html = TreesitterTool().render_html_section(data, top_n=2)
    assert "f0.py" in html
    assert "f2.py" not in html
