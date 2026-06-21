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
