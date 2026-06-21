from unittest.mock import patch, MagicMock
from src.tools.flake8_tool import Flake8Tool

@patch("subprocess.run")
def test_run_flake8_parses_text(mock_run, tmp_path):
    fake_flake8_output = "src/app.py:10:5: E302 expected 2 blank lines, found 1\nsrc/utils.py:42:1: W293 blank line contains whitespace"
    
    mock_result = MagicMock()
    mock_result.stdout = fake_flake8_output
    mock_run.return_value = mock_result
    
    result = Flake8Tool().run(tmp_path)
    
    assert len(result) == 2
    assert result[0]["file"] == "src/app.py"
    assert "E302 expected 2 blank lines" in result[0]["issue"]
    assert result[1]["file"] == "src/utils.py"


@patch("subprocess.run")
def test_run_flake8_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result
    
    result = Flake8Tool().run(tmp_path)
    assert result == []
