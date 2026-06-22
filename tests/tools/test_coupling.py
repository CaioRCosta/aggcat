from rich.console import Console

from src.tools.coupling_tool import CouplingTool


def test_run_detects_fan_out(tmp_path):
    (tmp_path / "a.py").write_text("from b import x\n")
    (tmp_path / "b.py").write_text("x = 1\n")
    result = CouplingTool().run(tmp_path)
    by_module = {r["module"]: r for r in result}
    assert by_module["a"]["fan_out"] == 1
    assert by_module["b"]["fan_in"] == 1


def test_run_ignores_external_imports(tmp_path):
    (tmp_path / "a.py").write_text("import os\nimport requests\n")
    result = CouplingTool().run(tmp_path)
    by_module = {r["module"]: r for r in result}
    assert by_module["a"]["fan_out"] == 0


def test_run_skips_venv(tmp_path):
    venv = tmp_path / "venv"
    venv.mkdir()
    (venv / "pkg.py").write_text("x = 1\n")
    (tmp_path / "a.py").write_text("x = 1\n")
    result = CouplingTool().run(tmp_path)
    assert all("venv" not in r["module"] for r in result)


def test_run_empty_repo(tmp_path):
    result = CouplingTool().run(tmp_path)
    assert result == []


def test_run_sorts_by_total_coupling_descending(tmp_path):
    (tmp_path / "a.py").write_text("from b import x\nfrom c import y\n")
    (tmp_path / "b.py").write_text("x = 1\n")
    (tmp_path / "c.py").write_text("y = 1\n")
    result = CouplingTool().run(tmp_path)
    totals = [r["fan_in"] + r["fan_out"] for r in result]
    assert totals == sorted(totals, reverse=True)


def test_render_terminal_empty_does_not_print():
    from unittest.mock import MagicMock
    console = MagicMock()
    CouplingTool().render_terminal([], console, top_n=10)
    console.print.assert_not_called()


def test_render_terminal_shows_data(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"module": "src.foo", "fan_out": 3, "fan_in": 1}]
    CouplingTool().render_terminal(data, console, top_n=10)
    out = (tmp_path / "out.txt").read_text()
    assert "src.foo" in out


def test_render_terminal_respects_top_n(tmp_path):
    console = Console(file=open(tmp_path / "out.txt", "w"))
    data = [{"module": f"mod{i}", "fan_out": i, "fan_in": 0} for i in range(5)]
    CouplingTool().render_terminal(data, console, top_n=2)
    out = (tmp_path / "out.txt").read_text()
    assert "mod0" in out
    assert "mod2" not in out


def test_render_html_empty():
    assert "No data." in CouplingTool().render_html_section([], top_n=10)


def test_render_html_contains_data():
    data = [{"module": "src.foo", "fan_out": 3, "fan_in": 1}]
    html = CouplingTool().render_html_section(data, top_n=10)
    assert "src.foo" in html


def test_render_html_respects_top_n():
    data = [{"module": f"mod{i}", "fan_out": i, "fan_in": 0} for i in range(5)]
    html = CouplingTool().render_html_section(data, top_n=2)
    assert "mod0" in html
    assert "mod2" not in html
