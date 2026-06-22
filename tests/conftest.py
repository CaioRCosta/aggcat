import pytest

from src.analyzer import SELECTABLE
from src.pipeline import AnalysisResult
from src.composites.hotspots import HotspotsReport
from src.composites.truck_factor import TruckFactorReport


@pytest.fixture
def empty_result():
    return AnalysisResult(repo_path="/fake/repo", selected_renderables=SELECTABLE)


@pytest.fixture
def full_result():
    hotspot_data = [
        {"file": "src/a.py", "churn": 42, "cc": 18},
        {"file": "src/b.py", "churn": 31, "cc": 14},
    ]
    truck_data = [
        {"file": "src/a.py", "authors": 1, "commits": 87},
        {"file": "src/b.py", "authors": 2, "commits": 20},
    ]
    return AnalysisResult(
        repo_path="/fake/repo",
        static={
            "radon": [
                {"file": "src/a.py", "mi": 85.0},
                {"file": "src/b.py", "mi": 55.0},
                {"file": "src/c.py", "mi": 30.0},
            ],
            "bandit": [
                {"file": "src/a.py", "severity": "HIGH", "issue_text": "hardcoded password"},
                {"file": "src/b.py", "severity": "LOW", "issue_text": "use of assert"},
            ],
        },
        composite={
            "hotspots": hotspot_data,
            "truck_factor": truck_data,
        },
        selected_renderables=SELECTABLE,
    )
