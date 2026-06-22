import os
from pathlib import Path
from src.tools.radon_tool import RadonTool
from src.tools.bandit_tool import BanditTool
from src.tools.vulture_tool import VultureTool
from src.tools.flake8_tool import Flake8Tool
from src.tools.lizard_tool import LizardTool
from src.tools.ast_nesting_tool import AstNestingTool

TOOLS = [
    RadonTool(),
    BanditTool(),
    VultureTool(),
    Flake8Tool(),
    LizardTool(),
    AstNestingTool()
]

def _has_github_token() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN", "").strip())

def run(repo_path: str | Path, selected_tools: list = None) -> dict:
    path = Path(repo_path).resolve()
    has_token = _has_github_token()
    tools_to_run = selected_tools if selected_tools is not None else TOOLS
    results = {}
    for tool in tools_to_run:
        if tool.requires_github and not has_token:
            continue
        results[tool.name] = tool.run(path)
    return results