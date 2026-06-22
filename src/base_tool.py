from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from src.config import load_config

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def defaults(self) -> Dict[str, Any]:
        return {}

    def _get_config(self, key: str) -> Any:
        return load_config().get(self.name, {}).get(key, self.defaults.get(key))

    @property
    def requires_github(self) -> bool:
        return False

    @property
    def renderable(self) -> bool:
        return type(self).render_terminal is not BaseTool.render_terminal

    @abstractmethod
    def run(self, repo_path: Path) -> List[Dict[str, Any]]:
        pass

    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        pass

    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        return ""
