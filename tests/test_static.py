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