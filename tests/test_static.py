"""Testes de unidade para o módulo de análise estática"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from aggcat.static import analyzer


@patch("aggcat.static.analyzer.run_radon")
def test_run_returns_correct_structure(mock_radon, tmp_path):
    mock_radon.return_value = [{"file": "main.py", "mi": 85.0}]
    
    result = analyzer.run(tmp_path)
    
    assert "maintainability" in result
    assert "security" in result
    assert result["maintainability"][0]["mi"] == 85.0
    assert result["security"] == []


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