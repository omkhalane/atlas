"""
Unit tests for ExecutionScope deadline/cancellation semantics.
"""
import asyncio
import copy
import time
import pytest

from core.python.agents.core_types.scope import ExecutionScope
from core.python.agents.core_types.errors import ExecutionCancelledError


def make_scope(**kwargs):
    defaults = dict(
        agent_id="agent-1",
        session_id="sess-1",
        workspace_id="ws-1",
        execution_id="exec-1",
        conversation_id="conv-1",
    )
    defaults.update(kwargs)
    return ExecutionScope.create(**defaults)


# ── 1. Deadline inheritance ──────────────────────────────
def test_child_inherits_parent_deadline():
    parent = make_scope(deadline_seconds=60.0)
    child = ExecutionScope.child_of(parent, agent_id="worker-1")
    assert abs(child._deadline_monotonic - parent._deadline_monotonic) < 1e-6


# ── 2. Child cannot extend deadline ──────────────────────
def test_child_remaining_lte_parent():
    parent = make_scope(deadline_seconds=10.0)
    time.sleep(0.05)
    child = ExecutionScope.child_of(parent, agent_id="worker-1")
    assert child.remaining() <= parent.remaining() + 0.01


# ── 3. Shared cancellation signal ────────────────────────
def test_cancel_propagates_to_child():
    parent = make_scope(deadline_seconds=60.0)
    child = ExecutionScope.child_of(parent, agent_id="worker-1")
    assert not child.is_cancelled()
    parent.cancel()
    assert child.is_cancelled()


# ── 4. check_cancellation raises on cancelled ────────────
def test_check_cancellation_raises():
    scope = make_scope(deadline_seconds=60.0)
    scope.cancel()
    with pytest.raises(ExecutionCancelledError):
        scope.check_cancellation()


# ── 5. Expired deadline triggers cancellation ────────────
def test_expired_deadline_raises():
    scope = make_scope(deadline_seconds=0.0)
    with pytest.raises(ExecutionCancelledError):
        scope.check_cancellation()


# ── 6. Already expired on call ───────────────────────────
def test_remaining_zero_when_expired():
    scope = make_scope(deadline_seconds=0.0)
    assert scope.remaining() == 0.0
    assert scope.is_expired()


# ── 7. Deep copy forbidden ────────────────────────────────
def test_deepcopy_raises():
    scope = make_scope()
    with pytest.raises(TypeError, match="must not be deep-copied"):
        copy.deepcopy(scope)


# ── 8. Timed executor timeout ────────────────────────────
@pytest.mark.asyncio
async def test_timed_executor_timeout():
    from packages.runtime.policy.timed_executor import TimedToolExecutor
    from core.python.contracts.tool import ToolResult

    class SlowExecutor:
        async def execute_tool(self, name, arguments):
            await asyncio.sleep(10)
            return ToolResult(result="done")

    scope = make_scope(deadline_seconds=0.05)
    wrapper = TimedToolExecutor(SlowExecutor(), scope)
    result = await wrapper.execute_tool("some_tool", {})
    assert result.error is not None
    assert "timed out" in result.error.lower() or "deadline" in result.error.lower()


# ── 9. Timed executor passes through on success ──────────
@pytest.mark.asyncio
async def test_timed_executor_success():
    from packages.runtime.policy.timed_executor import TimedToolExecutor
    from core.python.contracts.tool import ToolResult

    class FastExecutor:
        async def execute_tool(self, name, arguments):
            return ToolResult(result="42")

    scope = make_scope(deadline_seconds=30.0)
    wrapper = TimedToolExecutor(FastExecutor(), scope)
    result = await wrapper.execute_tool("calculator", {})
    assert result.result == "42"
    assert result.error is None


# ── 10. Concurrent child cancellation ────────────────────
@pytest.mark.asyncio
async def test_concurrent_cancellation():
    parent = make_scope(deadline_seconds=60.0)

    results = []

    async def child_task(agent_id):
        scope = ExecutionScope.child_of(parent, agent_id=agent_id)
        try:
            await asyncio.sleep(5)
            results.append("completed")
        except asyncio.CancelledError:
            results.append(f"cancelled-{agent_id}")
            raise

    tasks = [asyncio.create_task(child_task(f"w{i}")) for i in range(3)]
    await asyncio.sleep(0.05)
    parent.cancel()
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    assert all("cancelled" in r for r in results)
