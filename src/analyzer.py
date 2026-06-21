from pathlib import Path
from src.tools.radon_tool import RadonTool
from src.tools.bandit_tool import BanditTool
from src.tools.vulture_tool import VultureTool
from src.tools.flake8_tool import Flake8Tool
from src.tools.lizard_tool import LizardTool
from src.tools.ast_nesting_tool import AstNestingTool

# Registry of static analysis tools
TOOLS = [
    RadonTool(),
    BanditTool(),
    VultureTool(),
    Flake8Tool(),
    LizardTool(),
    AstNestingTool()
]

def run(repo_path: str | Path) -> dict:
    path = Path(repo_path).resolve()
    results = {}
    for tool in TOOLS:
        results[tool.name] = tool.run(path)
    return results