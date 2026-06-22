import os
from pathlib import Path
from src.tools.radon_tool import RadonTool
from src.tools.bandit_tool import BanditTool
from src.tools.vulture_tool import VultureTool
from src.tools.flake8_tool import Flake8Tool
from src.tools.lizard_tool import LizardTool
from src.tools.ast_nesting_tool import AstNestingTool
from src.tools.cloc_tool import ClocTool
from src.tools.pip_audit_tool import PipAuditTool
from src.tools.treesitter_tool import TreesitterTool
from src.tools.coverage_tool import CoverageTool
from src.tools.pydriller_tool import PyDrillerTool
from src.tools.gitpython_tool import GitPythonTool
from src.tools.coupling_tool import CouplingTool
from src.tools.github_tool import GithubTool
from src.composites.hotspots import HotspotsReport
from src.composites.uncovered_complex import UncoveredComplexReport
from src.composites.bandit_risk import BanditRiskReport
from src.composites.truck_factor import TruckFactorReport

ALL_BASE_TOOLS = [
    RadonTool(),
    BanditTool(),
    VultureTool(),
    Flake8Tool(),
    LizardTool(),
    AstNestingTool(),
    ClocTool(),
    PipAuditTool(),
    TreesitterTool(),
    CoverageTool(),
    PyDrillerTool(),
    GitPythonTool(),
    CouplingTool(),
    GithubTool(),
]

COMPOSITE_REPORTS = [
    HotspotsReport(),
    TruckFactorReport(),
    UncoveredComplexReport(),
    BanditRiskReport(),
]

# What appears in the interactive selector: renderable base tools + all composites
SELECTABLE = [t for t in ALL_BASE_TOOLS if t.renderable] + COMPOSITE_REPORTS

# Legacy alias used by report.py and tests
TOOLS = SELECTABLE


def _has_github_token() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN", "").strip())


def run(repo_path: str | Path, selected_tools: list = None) -> dict:
    path = Path(repo_path).resolve()
    has_token = _has_github_token()
    tools_to_run = selected_tools if selected_tools is not None else ALL_BASE_TOOLS
    results = {}
    for tool in tools_to_run:
        if tool.requires_github and not has_token:
            continue
        results[tool.name] = tool.run(path)
    return results