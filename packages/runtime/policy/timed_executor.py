"""
TimedToolExecutor — wraps IToolExecutor with deadline enforcement.

The concrete DockerToolExecutor is NOT modified. The deadline is
extracted from the ExecutionScope and applied via asyncio.timeout()
at the DI boundary, before the concrete executor runs.
"""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from core.python.contracts.tool import ToolResult
from core.python.agents.core_types.scope import ExecutionScope

if TYPE_CHECKING:
    from core.python.contracts.tool import IToolExecutor


class TimedToolExecutor:
    """Implements IToolExecutor (duck-typed)."""

    def __init__(self, inner: "IToolExecutor", scope: ExecutionScope) -> None:
        self._inner = inner
        self._scope = scope

    async def execute_tool(self, name: str, arguments: dict) -> ToolResult:
        remaining = self._scope.remaining()
        if remaining == 0.0:
            return ToolResult(result="", error="Execution deadline already exceeded.")
        try:
            async with asyncio.timeout(remaining):
                return await self._inner.execute_tool(name, arguments)
        except asyncio.TimeoutError:
            return ToolResult(result="", error=f"Tool '{name}' timed out after {remaining:.1f}s budget.")
        except asyncio.CancelledError:
            return ToolResult(result="", error=f"Tool '{name}' was cancelled.")
