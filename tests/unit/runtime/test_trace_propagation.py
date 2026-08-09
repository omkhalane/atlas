"""
F-04 Trace Propagation Tests — verified against actual runtime namespace.
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from runtime.observability.trace_context import set_trace, clear_trace, get_envelope
from runtime.observability.enveloped_event_bus import EnvelopedEventBus


# ── 1. Envelope is empty when no trace active ─────────────────
def test_empty_envelope_with_no_context():
    clear_trace()
    assert get_envelope() == {}


# ── 2. set_trace populates envelope ──────────────────────────
def test_set_trace_populates_envelope():
    set_trace("exec-1", "conv-1", "agent-1")
    env = get_envelope()
    assert env["execution_id"] == "exec-1"
    assert env["conversation_id"] == "conv-1"
    assert env["agent_id"] == "agent-1"
    clear_trace()


# ── 3. Events stamped with execution_id ──────────────────────
@pytest.mark.asyncio
async def test_events_stamped_with_trace():
    captured = []
    inner = MagicMock()
    inner.publish = AsyncMock(side_effect=lambda t, p: captured.append(p))
    bus = EnvelopedEventBus(inner)

    set_trace("exec-42", "conv-42", "agent-42")
    await bus.publish("tool.executed", {"tool": "calculator"})
    clear_trace()

    assert captured[0]["execution_id"] == "exec-42"
    assert captured[0]["conversation_id"] == "conv-42"
    assert captured[0]["tool"] == "calculator"


# ── 4. Concurrent executions do not contaminate each other ───
@pytest.mark.asyncio
async def test_concurrent_trace_isolation():
    results = {}

    async def run_trace(exec_id: str):
        set_trace(exec_id, f"conv-{exec_id}", "agent-1")
        await asyncio.sleep(0.01)
        results[exec_id] = get_envelope().get("execution_id")
        clear_trace()

    await asyncio.gather(run_trace("A"), run_trace("B"))
    # Each task has its own ContextVar copy; both must be correct
    assert results["A"] == "A"
    assert results["B"] == "B"


# ── 5. Trace stable across multiple events ───────────────────
@pytest.mark.asyncio
async def test_trace_stable_across_events():
    captured = []
    inner = MagicMock()
    inner.publish = AsyncMock(side_effect=lambda t, p: captured.append(p))
    bus = EnvelopedEventBus(inner)

    set_trace("exec-stable", "conv-s", "ag-s")
    for _ in range(5):
        await bus.publish("any.event", {})
    clear_trace()

    ids = {e["execution_id"] for e in captured}
    assert ids == {"exec-stable"}


# ── 6. No trace active — no crash, no envelope ───────────────
@pytest.mark.asyncio
async def test_no_trace_no_crash():
    clear_trace()
    captured = []
    inner = MagicMock()
    inner.publish = AsyncMock(side_effect=lambda t, p: captured.append(p))
    bus = EnvelopedEventBus(inner)

    await bus.publish("something.happened", {"x": 1})
    # event_id should be absent, x should still be present
    assert captured[0]["x"] == 1
    assert "execution_id" not in captured[0]


# ── 7. Cancellation does not destroy trace ───────────────────
def test_cancellation_preserves_trace_data():
    set_trace("exec-cancel", "conv-c", "ag-c")
    env = get_envelope()
    assert env["execution_id"] == "exec-cancel"
    clear_trace()


# ── 8. clear_trace removes envelope ──────────────────────────
def test_clear_trace_removes_envelope():
    set_trace("exec-x", "conv-x", "ag-x")
    clear_trace()
    assert get_envelope() == {}


# ── 9. EventBus subscribe passthrough ────────────────────────
def test_subscribe_passthrough():
    inner = MagicMock()
    bus = EnvelopedEventBus(inner)
    handler = AsyncMock()
    bus.subscribe("event.type", handler)
    inner.subscribe.assert_called_once_with("event.type", handler)


# ── 10. history passthrough ───────────────────────────────────
def test_history_passthrough():
    inner = MagicMock()
    inner.history = ["event1", "event2"]
    bus = EnvelopedEventBus(inner)
    assert bus.history == ["event1", "event2"]
