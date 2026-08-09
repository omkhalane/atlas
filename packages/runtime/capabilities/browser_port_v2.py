"""
BrowserPortV2 — implements IBrowserSession backed by BrowserSessionPool.

Each instance is bound to one ExecutionScope. acquire() is called lazily
on first use. release() must be called on scope completion.

Playwright is NEVER exposed to core. All Playwright types remain inside
this integration-layer class.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from playwright.async_api import Page, Error as PlaywrightError

from core.python.agents.core_types.scope import ExecutionScope
from core.python.agents.core_types.errors import ExecutionCancelledError
from packages.runtime.capabilities.browser_session_pool import BrowserSessionPool

logger = logging.getLogger(__name__)


class BrowserPortV2:
    """Implements IBrowserSession (duck-typed). Playwright stays inside."""

    def __init__(self, pool: BrowserSessionPool, scope: ExecutionScope) -> None:
        self._pool = pool
        self._scope = scope
        self._page: Optional[Page] = None
        self._released = False

    async def _get_page(self) -> Page:
        """Lazily acquire a page. Reconnect if the slot crashed."""
        if self._released:
            raise RuntimeError("BrowserPortV2: session already released.")
        self._scope.check_cancellation()
        self._page = await self._pool.acquire(self._scope)
        return self._page

    async def _run(self, coro) -> Any:
        """Run a coroutine with deadline + crash guard."""
        remaining = self._scope.remaining()
        if remaining == 0.0:
            from core.python.contracts.tool import ToolResult
            return ToolResult(result="", error="Browser deadline already exceeded.")
        try:
            async with asyncio.timeout(remaining):
                return await coro
        except asyncio.TimeoutError:
            from core.python.contracts.tool import ToolResult
            return ToolResult(result="", error=f"Browser action timed out ({remaining:.1f}s budget).")
        except asyncio.CancelledError:
            from core.python.contracts.tool import ToolResult
            return ToolResult(result="", error="Browser action cancelled.")
        except PlaywrightError as exc:
            from core.python.contracts.tool import ToolResult
            logger.error(f"Playwright error: {exc}")
            return ToolResult(result="", error=f"Browser error: {exc}")

    async def navigate(self, url: str, **kwargs) -> Any:
        page = await self._get_page()
        return await self._run(page.goto(url, **kwargs))

    async def click(self, selector: str, **kwargs) -> Any:
        page = await self._get_page()
        return await self._run(page.click(selector, **kwargs))

    async def type_text(self, selector: str, text: str, **kwargs) -> Any:
        page = await self._get_page()
        return await self._run(page.fill(selector, text, **kwargs))

    async def get_content(self, **kwargs) -> str:
        page = await self._get_page()
        result = await self._run(page.content(**kwargs))
        return result if isinstance(result, str) else ""

    async def screenshot(self, **kwargs) -> bytes:
        page = await self._get_page()
        result = await self._run(page.screenshot(**kwargs))
        return result if isinstance(result, bytes) else b""

    async def evaluate(self, script: str, **kwargs) -> Any:
        page = await self._get_page()
        return await self._run(page.evaluate(script, **kwargs))

    async def close(self) -> None:
        """Release this agent's context back to the pool."""
        if self._released:
            return
        self._released = True
        await self._pool.release(self._scope)
