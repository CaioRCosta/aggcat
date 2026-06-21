from unittest.mock import patch, MagicMock

from src.tools.lizard_tool import LizardTool


@patch("subprocess.run")
def test_run_lizard_parses_warnings(mock_run, tmp_path):
    fake_output = "src/math.py:50: warning: process_data has 12 CCN\nsrc/api.py:10: warning: route has 22 CCN"
    mock_result = MagicMock()
    mock_result.stdout = fake_output
    mock_run.return_value = mock_result

    result = LizardTool().run(tmp_path)

    assert len(result) == 2
    assert result[0]["file"] == "src/math.py:50"
    assert "12 CCN" in result[0]["issue"]


@patch("subprocess.run")
def test_run_lizard_empty_output(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    result = LizardTool().run(tmp_path)
    assert result == []
