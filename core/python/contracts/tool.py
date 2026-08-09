from typing import Protocol
from dataclasses import dataclass

@dataclass(frozen=True)
class ToolResult:
    result: str
    error: str | None = None

class IToolExecutor(Protocol):
    async def execute_tool(
        self,
        name: str,
        arguments: dict,
    ) -> ToolResult:
        ...
