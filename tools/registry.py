from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict                       # JSON schema
    handler: Callable[..., Awaitable[Any]]  # async callable
    dangerous: bool = False                 # requires confirmation
    category: str = "general"


@dataclass
class ToolRegistry:
    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        return list(self._tools.values())

    def categories(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for t in self._tools.values():
            out.setdefault(t.category, []).append(t.name)
        return out

    def openai_schema(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]
