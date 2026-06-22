from unittest.mock import MagicMock

from rich.console import Console

from src.tools.ast_nesting_tool import AstNestingTool


def test_run_ast_nesting_detects_deep_nesting(tmp_path):
    code = '''
def complex_function():
    if True:
        for i in range(10):
            while True:
                try:
                    pass
                except:
                    pass
'''
    (tmp_path / "deep.py").write_text(code, encoding="utf-8")

    result = AstNestingTool().run(tmp_path)

    assert len(result) == 1
    assert result[0]["file"] == "deep.py"
    assert "depth: 4" in result[0]["issue"]


def test_run_ast_nesting_ignores_shallow_code(tmp_path):
    code = '''
def simple_function():
    if True:
        pass
'''
    (tmp_path / "simple.py").write_text(code, encoding="utf-8")

    result = AstNestingTool().run(tmp_path)

    assert len(result) == 0


def test_run_ast_nesting_ignores_syntax_errors(tmp_path):
    (tmp_path / "broken.py").write_text("def quebrado(:::", encoding="utf-8")

    result = AstNestingTool().run(tmp_path)

    assert len(result) == 0


def test_run_ast_nesting_skips_venv_directory(tmp_path):
    venv_dir = tmp_path / "venv" / "lib"
    venv_dir.mkdir(parents=True)
    code = '''
def f():
    if True:
        for i in range(10):
            while True:
                try:
                    pass
                except:
                    pass
'''
    (venv_dir / "deep.py").write_text(code, encoding="utf-8")

    result = AstNestingTool().run(tmp_path)
    assert len(result) == 0


def test_run_ast_nesting_multiple_files(tmp_path):
    deep_code = '''
def f():
    if True:
        for i in range(10):
            while True:
                try:
                    pass
                except:
                    pass
'''
    shallow_code = "x = 1\n"
    (tmp_path / "deep.py").write_text(deep_code, encoding="utf-8")
    (tmp_path / "shallow.py").write_text(shallow_code, encoding="utf-8")

    result = AstNestingTool().run(tmp_path)
    assert len(result) == 1
    assert result[0]["file"] == "deep.py"


def test_render_terminal_empty_data_does_not_print():
    console = MagicMock()
    AstNestingTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_issues(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": "deep.py", "issue": "Deep nesting detected (depth: 4)"}]
    AstNestingTool().render_terminal(data, console, top_n=10)
    output = (tmp_path / "out.txt").read_text()
    assert "deep.py" in output
    assert "depth: 4" in output


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"file": f"src/{i}.py", "issue": "Deep nesting detected (depth: 5)"} for i in range(5)]
    AstNestingTool().render_terminal(data, console, top_n=2)
    output = (tmp_path / "out.txt").read_text()
    assert "src/0.py" in output
    assert "src/2.py" not in output


def test_render_html_empty_returns_no_data():
    html = AstNestingTool().render_html_section([], top_n=10)
    assert "No data." in html


def test_render_html_contains_file():
    data = [{"file": "deep.py", "issue": "Deep nesting detected (depth: 4)"}]
    html = AstNestingTool().render_html_section(data, top_n=10)
    assert "deep.py" in html


def test_render_html_respects_top_n():
    data = [{"file": f"src/{i}.py", "issue": "deep"} for i in range(5)]
    html = AstNestingTool().render_html_section(data, top_n=2)
    assert "src/0.py" in html
    assert "src/2.py" not in html
