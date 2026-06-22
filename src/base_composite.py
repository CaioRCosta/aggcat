from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING
from rich.console import Console
from src.config import load_config

if TYPE_CHECKING:
    from src.base_tool import BaseTool


class CompositeReport(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def depends_on(self) -> List["BaseTool"]:
        """BaseTool instances this report requires."""
        pass

    @property
    def defaults(self) -> Dict[str, Any]:
        return {}

    def _get_config(self, key: str) -> Any:
        return load_config().get(self.name, {}).get(key, self.defaults.get(key))

    @property
    def requires_github(self) -> bool:
        return any(t.requires_github for t in self.depends_on)

    @property
    def full_description(self) -> str:
        deps = ", ".join(t.name for t in self.depends_on)
        return f"{self.description} \\[uses: {deps}]"

    @abstractmethod
    def run(self, static: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def render_terminal(self, data: List[Dict[str, Any]], console: Console, top_n: int | None) -> None:
        pass

    @abstractmethod
    def render_html_section(self, data: List[Dict[str, Any]], top_n: int | None) -> str:
        pass
