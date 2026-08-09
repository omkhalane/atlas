"""
BrowserSessionPool — allocates one Playwright BrowserContext + Page
per (execution_id, agent_id) composite key.

IDENTITY KEY DECISION:
  execution_id alone is NOT sufficient — Supervisor and Workers share
  the same execution_id. The composite key (execution_id, agent_id)
  ensures one context per agent per run.

Lifecycle:
  acquire(scope)  → creates or returns existing context/page for scope
  release(scope)  → closes context/page; removes from pool
  release_all()   → closes everything (called on runtime shutdown)

Thread/concurrency safety:
  asyncio.Lock per composite key prevents double-initialisation under
  concurrent acquire() calls for the same agent.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    async_playwright,
    Playwright,
)

from core.python.agents.core_types.scope import ExecutionScope
from core.python.contracts.events import IEventBus

logger = logging.getLogger(__name__)

# Composite isolation key
_SessionKey = Tuple[str, str]   # (execution_id, agent_id)


@dataclass
class _BrowserSlot:
    context: BrowserContext
    page: Page
    crashed: bool = False
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)


class BrowserSessionPool:
    """
    Manages per-agent browser contexts backed by a shared Playwright Browser.
    One Playwright + Browser instance is shared; each agent gets its own Context.
    """

    def __init__(self, event_bus: IEventBus) -> None:
        self._event_bus = event_bus
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._slots: Dict[_SessionKey, _BrowserSlot] = {}
        self._slot_locks: Dict[_SessionKey, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._browser_crashed = False

    # ── Lifecycle ──────────────────────────────────────────────

    async def _ensure_browser(self) -> Browser:
        """Launch Playwright + Browser if not running. Reconnect after crash."""
        if self._browser and not self._browser_crashed:
            return self._browser
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._browser.on("disconnected", self._on_browser_disconnected)
        self._browser_crashed = False
        logger.info("Browser process launched.")
        await self._event_bus.publish("browser.launched", {})
        return self._browser

    def _on_browser_disconnected(self, browser) -> None:
        self._browser_crashed = True
        logger.error("Browser process disconnected.")
        self._event_bus.publish_sync("browser.crashed", {"all_sessions_invalidated": True})
        # Mark all slots as crashed
        for slot in self._slots.values():
            slot.crashed = True

    # ── Acquire ────────────────────────────────────────────────

    async def acquire(self, scope: ExecutionScope) -> Page:
        """
        Acquire a Page for this scope. Creates a new BrowserContext if needed.
        Safe to call concurrently for the same scope — lock prevents double-init.
        """
        key: _SessionKey = (scope.execution_id, scope.agent_id)

        # Per-key lock: serialises concurrent acquire() for the same agent
        async with self._global_lock:
            if key not in self._slot_locks:
                self._slot_locks[key] = asyncio.Lock()
        
        async with self._slot_locks[key]:
            slot = self._slots.get(key)
            if slot and not slot.crashed:
                return slot.page

            # Slot is missing or crashed — create a fresh context/page
            browser = await self._ensure_browser()
            context = await browser.new_context()
            page = await context.new_page()

            # Crash handlers
            page.on("crash", lambda _: self._on_page_crash(key))
            context.on("close", lambda _: self._on_context_close(key))

            slot = _BrowserSlot(context=context, page=page)
            self._slots[key] = slot

            logger.info(f"Browser session acquired: {key}")
            await self._event_bus.publish("browser.session.acquired", {
                "execution_id": scope.execution_id,
                "agent_id": scope.agent_id,
            })
            return page

    # ── Crash handlers ─────────────────────────────────────────

    def _on_page_crash(self, key: _SessionKey) -> None:
        slot = self._slots.get(key)
        if slot:
            slot.crashed = True
        logger.error(f"Page crashed for session {key}")
        self._event_bus.publish_sync("browser.page.crashed", {"key": str(key)})

    def _on_context_close(self, key: _SessionKey) -> None:
        self._slots.pop(key, None)
        logger.info(f"Browser context closed for session {key}")
        self._event_bus.publish_sync("browser.context.closed", {"key": str(key)})

    # ── Release ────────────────────────────────────────────────

    async def release(self, scope: ExecutionScope) -> None:
        """Release the context/page for this scope. Safe to call after crash."""
        key: _SessionKey = (scope.execution_id, scope.agent_id)
        lock = self._slot_locks.get(key)
        if lock is None:
            return

        async with lock:
            slot = self._slots.pop(key, None)
            if slot is None:
                return
            try:
                await slot.context.close()
            except Exception as exc:
                logger.warning(f"Error closing context for {key}: {exc}")
            finally:
                self._slot_locks.pop(key, None)
                logger.info(f"Browser session released: {key}")
                await self._event_bus.publish("browser.session.released", {
                    "execution_id": scope.execution_id,
                    "agent_id": scope.agent_id,
                })

    async def release_all(self) -> None:
        """Release every slot. Called on runtime shutdown."""
        keys = list(self._slots.keys())
        for key in keys:
            slot = self._slots.pop(key, None)
            if slot:
                try:
                    await slot.context.close()
                except Exception:
                    pass
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
        logger.info("All browser sessions released.")
        await self._event_bus.publish("browser.pool.shutdown", {})
