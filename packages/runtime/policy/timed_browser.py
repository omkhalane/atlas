"""
TimedBrowserWrapper — wraps IBrowserSession with deadline enforcement.
"""
from __future__ import annotations

import asyncio
from typing import Any, TYPE_CHECKING

from core.python.contracts.tool import ToolResult
from core.python.agents.core_types.scope import ExecutionScope

if TYPE_CHECKING:
    from core.python.contracts.browser import IBrowserSession


class TimedBrowserWrapper:
    """Implements IBrowserSession (duck-typed)."""

    def __init__(self, inner: "IBrowserSession", scope: ExecutionScope) -> None:
        self._inner = inner
        self._scope = scope

    async def navigate(self, url: str, **kwargs: Any) -> Any:
        return await self._timed(self._inner.navigate(url, **kwargs))

    async def click(self, selector: str, **kwargs: Any) -> Any:
        return await self._timed(self._inner.click(selector, **kwargs))

    async def _timed(self, coro):
        remaining = self._scope.remaining()
        if remaining == 0.0:
            return ToolResult(result="", error="Browser deadline already exceeded.")
        try:
            async with asyncio.timeout(remaining):
                return await coro
        except asyncio.TimeoutError:
            return ToolResult(result="", error=f"Browser action timed out after {remaining:.1f}s budget.")

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
