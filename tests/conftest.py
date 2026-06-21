import pytest

from src.pipeline import AnalysisResult


@pytest.fixture
def empty_result():
    return AnalysisResult(repo_path="/fake/repo")


@pytest.fixture
def full_result():
    return AnalysisResult(
        repo_path="/fake/repo",
        static={
            "maintainability": [
                {"file": "src/a.py", "mi": 85.0},
                {"file": "src/b.py", "mi": 55.0},
                {"file": "src/c.py", "mi": 30.0},
            ],
            "security": [
                {"file": "src/a.py", "severity": "HIGH", "issue": "hardcoded password"},
                {"file": "src/b.py", "severity": "LOW", "issue": "use of assert"},
            ],
        },
        git={
            "hotspots": [
                {"file": "src/a.py", "churn": 42, "complexity": 18},
                {"file": "src/b.py", "churn": 31, "complexity": 14},
            ],
            "truck_factor": [
                {"file": "src/a.py", "authors": 1, "commits": 87},
                {"file": "src/b.py", "authors": 3, "commits": 20},
            ],
        },
    )
