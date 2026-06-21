"""Testes de unidade para o módulo de análise estática"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.static import analyzer

@patch("subprocess.run")
def test_run_radon_parses_json(mock_run, tmp_path):
    fake_radon_output = json.dumps({
        "src/app.py": {"mi": 45.33333, "rank": "C"}
    })
    
    mock_result = MagicMock()
    mock_result.stdout = fake_radon_output
    mock_run.return_value = mock_result
    
    result = analyzer.run_radon(tmp_path)
    
    assert len(result) == 1
    assert result[0]["file"] == "src/app.py"
    assert result[0]["mi"] == 45.33

@patch("subprocess.run")
def test_run_radon_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = " "
    mock_run.return_value = mock_result
    
    result = analyzer.run_radon(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_bandit_parses_json(mock_run, tmp_path):
    fake_bandit_output = json.dumps({
        "results": [
            {
                "filename": "auth.py",
                "issue_severity": "HIGH",
                "issue_text": "Hardcoded password"
            }
        ]
    })
    mock_result = MagicMock()
    mock_result.stdout = fake_bandit_output
    mock_run.return_value = mock_result
    
    result = analyzer.run_bandit(tmp_path)
    
    assert len(result) == 1
    assert result[0]["severity"] == "HIGH"
    assert "Hardcoded" in result[0]["issue"]

@patch("subprocess.run")
def test_run_bandit_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result
    
    result = analyzer.run_bandit(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_vulture_parses_text(mock_run, tmp_path):
    fake_vulture_output = "src/utils.py:15: unused function 'helper' (60%)\nsrc/main.py:42: unused import 'os' (100%)"
    
    mock_result = MagicMock()
    mock_result.stdout = fake_vulture_output
    mock_run.return_value = mock_result
    
    result = analyzer.run_vulture(tmp_path)
    
    assert len(result) == 2
    assert result[0]["file"] == "src/utils.py"
    assert "unused function 'helper'" in result[0]["issue"]
    assert result[1]["file"] == "src/main.py"

@patch("subprocess.run")
def test_run_vulture_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result
    
    result = analyzer.run_vulture(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_flake8_parses_text(mock_run, tmp_path):
    fake_flake8_output = "src/app.py:10:5: E302 expected 2 blank lines, found 1\nsrc/utils.py:42:1: W293 blank line contains whitespace"
    
    mock_result = MagicMock()
    mock_result.stdout = fake_flake8_output
    mock_run.return_value = mock_result
    
    result = analyzer.run_flake8(tmp_path)
    
    assert len(result) == 2
    assert result[0]["file"] == "src/app.py"
    assert "E302 expected 2 blank lines" in result[0]["issue"]
    assert result[1]["file"] == "src/utils.py"

@patch("subprocess.run")
def test_run_flake8_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result
    
    result = analyzer.run_flake8(tmp_path)
    assert result == []


@patch("subprocess.run")
def test_run_lizard_parses_warnings(mock_run, tmp_path):
    fake_lizard_output = "src/math.py:50: warning: process_data has 12 CCN\nsrc/api.py:10: warning: route has 22 CCN"
    
    mock_result = MagicMock()
    mock_result.stdout = fake_lizard_output
    mock_run.return_value = mock_result
    
    result = analyzer.run_lizard(tmp_path)
    
    assert len(result) == 2
    assert result[0]["file"] == "src/math.py:50"
    assert "12 CCN" in result[0]["issue"]

@patch("subprocess.run")
def test_run_lizard_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result
    
    result = analyzer.run_lizard(tmp_path)
    assert result == []


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
    test_file = tmp_path / "deep.py"
    test_file.write_text(code, encoding="utf-8")
    
    result = analyzer.run_ast_nesting(tmp_path)
    
    assert len(result) == 1
    assert result[0]["file"] == "deep.py"
    assert "profundidade: 4" in result[0]["issue"]


def test_run_ast_nesting_ignores_shallow_code(tmp_path):
    code = '''
def simple_function():
    if True:
        pass
'''
    test_file = tmp_path / "simple.py"
    test_file.write_text(code, encoding="utf-8")
    
    result = analyzer.run_ast_nesting(tmp_path)
    
    assert len(result) == 0


def test_run_ast_nesting_ignores_syntax_errors(tmp_path):
    test_file = tmp_path / "broken.py"
    test_file.write_text("def quebrado(:::", encoding="utf-8")
    
    result = analyzer.run_ast_nesting(tmp_path)
    
    assert len(result) == 0