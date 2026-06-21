"""Testes de unidade para o módulo de análise estática"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from aggcat.static import analyzer

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