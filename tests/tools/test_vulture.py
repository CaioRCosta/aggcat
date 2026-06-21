from unittest.mock import patch, MagicMock
from src.tools.vulture_tool import VultureTool

@patch("subprocess.run")
def test_run_vulture_parses_text(mock_run, tmp_path):
    fake_vulture_output = "src/utils.py:15: unused function 'helper' (60%)\nsrc/main.py:42: unused import 'os' (100%)"
    
    mock_result = MagicMock()
    mock_result.stdout = fake_vulture_output
    mock_run.return_value = mock_result
    
    result = VultureTool().run(tmp_path)
    
    assert len(result) == 2
    assert result[0]["file"] == "src/utils.py"
    assert "unused function 'helper'" in result[0]["issue"]
    assert result[1]["file"] == "src/main.py"


@patch("subprocess.run")
def test_run_vulture_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result
    
    result = VultureTool().run(tmp_path)
    assert result == []
