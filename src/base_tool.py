from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The key representing the metric/tool output in the result dictionary."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of the tool and what it measures."""
        pass

    @property
    def defaults(self) -> Dict[str, Any]:
        """Default configuration parameters for the tool."""
        return {}

    @abstractmethod
    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Executes the analysis tool and returns a list of dictionaries with results."""
        pass

    @abstractmethod
    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        """Renders the tool results as a section in the terminal report."""
        pass

    @abstractmethod
    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        """Renders the tool results as an HTML section (including h2, table, and rows)."""
        pass
