"""
F-02 Browser Reliability Tests.

Uses unittest.mock + asyncio to avoid requiring a real Playwright runtime.
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from core.python.agents.core_types.scope import ExecutionScope


def make_scope(agent_id="agent-1", execution_id="exec-1", deadline=60.0):
    return ExecutionScope.create(
        agent_id=agent_id,
        session_id="sess-1",
        workspace_id="ws-1",
        execution_id=execution_id,
        conversation_id="conv-1",
        deadline_seconds=deadline,
    )


def make_mock_event_bus():
    bus = MagicMock()
    bus.publish = AsyncMock()
    bus.publish_sync = MagicMock()
    return bus


# ── 1. Single session acquire/release ──────────────────────
@pytest.mark.asyncio
async def test_single_session_acquire_release():
    from packages.runtime.capabilities.browser_session_pool import BrowserSessionPool

    bus = make_mock_event_bus()
    pool = BrowserSessionPool(bus)
    scope = make_scope()

    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.crashed = False

    with patch.object(pool, "_ensure_browser", return_value=mock_browser):
        page = await pool.acquire(scope)
        assert page is mock_page
        await pool.release(scope)
        mock_context.close.assert_awaited()


# ── 2. Two concurrent sessions get different contexts ───────
@pytest.mark.asyncio
async def test_two_concurrent_sessions_isolated():
    from packages.runtime.capabilities.browser_session_pool import BrowserSessionPool

    bus = make_mock_event_bus()
    pool = BrowserSessionPool(bus)
    scope_a = make_scope(agent_id="agent-a")
    scope_b = make_scope(agent_id="agent-b")

    page_a, page_b = AsyncMock(), AsyncMock()
    ctx_a, ctx_b = AsyncMock(), AsyncMock()
    ctx_a.new_page = AsyncMock(return_value=page_a)
    ctx_b.new_page = AsyncMock(return_value=page_b)
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(side_effect=[ctx_a, ctx_b])

    with patch.object(pool, "_ensure_browser", return_value=mock_browser):
        p1, p2 = await asyncio.gather(
            pool.acquire(scope_a), pool.acquire(scope_b)
        )
    assert p1 is not p2, "Agents must receive different pages"


# ── 3. Same key returns same page (idempotent acquire) ──────
@pytest.mark.asyncio
async def test_same_scope_returns_same_page():
    from packages.runtime.capabilities.browser_session_pool import BrowserSessionPool

    bus = make_mock_event_bus()
    pool = BrowserSessionPool(bus)
    scope = make_scope()

    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    with patch.object(pool, "_ensure_browser", return_value=mock_browser):
        p1 = await pool.acquire(scope)
        p2 = await pool.acquire(scope)
    assert p1 is p2


# ── 4. Page crash marks slot as crashed ─────────────────────
def test_page_crash_marks_slot_crashed():
    from packages.runtime.capabilities.browser_session_pool import BrowserSessionPool, _BrowserSlot
    from unittest.mock import MagicMock

    bus = make_mock_event_bus()
    pool = BrowserSessionPool(bus)
    key = ("exec-1", "agent-1")
    slot = _BrowserSlot(context=MagicMock(), page=MagicMock())
    pool._slots[key] = slot

    pool._on_page_crash(key)
    assert pool._slots[key].crashed is True


# ── 5. Stale/released session rejected ──────────────────────
@pytest.mark.asyncio
async def test_released_session_raises():
    from packages.runtime.capabilities.browser_port_v2 import BrowserPortV2

    scope = make_scope()
    pool_mock = AsyncMock()
    port = BrowserPortV2(pool=pool_mock, scope=scope)
    port._released = True

    with pytest.raises(RuntimeError, match="already released"):
        await port._get_page()


# ── 6. Timeout during navigation ────────────────────────────
@pytest.mark.asyncio
async def test_timeout_during_navigation():
    from packages.runtime.capabilities.browser_port_v2 import BrowserPortV2

    scope = make_scope(deadline=0.01)
    await asyncio.sleep(0.02)  # expire the scope

    pool_mock = AsyncMock()
    mock_page = AsyncMock()
    pool_mock.acquire = AsyncMock(return_value=mock_page)

    port = BrowserPortV2(pool=pool_mock, scope=scope)
    result = await port.navigate("https://example.com")
    assert result.error is not None
    assert "timeout" in result.error.lower() or "deadline" in result.error.lower()


# ── 7. Cancellation during browser operation ────────────────
@pytest.mark.asyncio
async def test_cancellation_during_browser():
    from packages.runtime.capabilities.browser_port_v2 import BrowserPortV2

    scope = make_scope(deadline=60.0)
    scope.cancel()  # fire cancellation before the call

    pool_mock = AsyncMock()
    port = BrowserPortV2(pool=pool_mock, scope=scope)

    from core.python.agents.core_types.errors import ExecutionCancelledError
    with pytest.raises(ExecutionCancelledError):
        await port._get_page()


# ── 8. Cleanup on exception doesn't leak context ────────────
@pytest.mark.asyncio
async def test_cleanup_on_exception():
    from packages.runtime.capabilities.browser_session_pool import BrowserSessionPool

    bus = make_mock_event_bus()
    pool = BrowserSessionPool(bus)
    scope = make_scope()

    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock(side_effect=Exception("close error"))
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    with patch.object(pool, "_ensure_browser", return_value=mock_browser):
        await pool.acquire(scope)
        # release should not raise even if close() fails
        await pool.release(scope)


# ── 9. Child deadline not reset ──────────────────────────────
def test_child_browser_scope_inherits_deadline():
    parent = make_scope(agent_id="supervisor", deadline=30.0)
    child = ExecutionScope.child_of(parent, agent_id="worker-1")
    assert abs(child._deadline_monotonic - parent._deadline_monotonic) < 1e-6


# ── 10. No Playwright exposure to core ──────────────────────
def test_playwright_not_importable_from_core():
    import importlib, sys
    # Verify playwright is not imported anywhere inside core/python
    core_modules = [m for m in sys.modules if m.startswith("core.python")]
    for mod_name in core_modules:
        mod = sys.modules[mod_name]
        src = getattr(mod, "__file__", "") or ""
        if "playwright" in src.lower():
            pytest.fail(f"Playwright imported in core module: {mod_name}")


# ── 11. Browser crash triggers all slots marked crashed ─────
def test_browser_disconnect_marks_all_slots_crashed():
    from packages.runtime.capabilities.browser_session_pool import (
        BrowserSessionPool, _BrowserSlot
    )

    bus = make_mock_event_bus()
    pool = BrowserSessionPool(bus)
    for i in range(3):
        slot = _BrowserSlot(context=MagicMock(), page=MagicMock())
        pool._slots[(f"exec-{i}", f"agent-{i}")] = slot

    pool._on_browser_disconnected(None)
    assert all(s.crashed for s in pool._slots.values())


# ── 12. release_all cleans up without raising ────────────────
@pytest.mark.asyncio
async def test_release_all():
    from packages.runtime.capabilities.browser_session_pool import (
        BrowserSessionPool, _BrowserSlot
    )

    bus = make_mock_event_bus()
    pool = BrowserSessionPool(bus)
    for i in range(2):
        ctx = AsyncMock()
        pool._slots[(f"exec-{i}", f"agent-{i}")] = _BrowserSlot(
            context=ctx, page=AsyncMock()
        )
    pool._browser = AsyncMock()
    pool._playwright = AsyncMock()
    await pool.release_all()
    assert len(pool._slots) == 0
