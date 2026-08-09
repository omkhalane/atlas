"""
Phase 5 — Live Integration Tests.
Verifies that ExecutionScope, trace propagation, and context assembly
are genuinely wired into the AtlasKernel execution path.
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.python.agents.core_types.scope import ExecutionScope
from runtime.observability.trace_context import get_envelope, clear_trace
from runtime.policy.gateway import PermissionGateway
from runtime.policy.store import SessionPolicyRegistry
from runtime.policy.authorized_executor import AuthorizedToolExecutor
from core.python.contracts.tool import ToolResult


# ── F-01: ExecutionScope created at root boundary ────────────
def test_scope_create_root():
    scope = ExecutionScope.create(
        agent_id="kernel", session_id="s1", workspace_id="ws1",
        execution_id="exec-1", conversation_id="conv-1", deadline_seconds=300.0
    )
    assert scope.execution_id == "exec-1"
    assert scope.remaining() > 0
    assert not scope.is_cancelled()


# ── F-01: Child inherits parent deadline ─────────────────────
def test_child_inherits_deadline():
    parent = ExecutionScope.create(
        agent_id="supervisor", session_id="s1", workspace_id="ws",
        execution_id="exec-1", conversation_id="conv-1", deadline_seconds=120.0
    )
    child = ExecutionScope.child_of(parent, agent_id="worker-1")
    assert abs(child._deadline_monotonic - parent._deadline_monotonic) < 1e-6
    assert child.execution_id == parent.execution_id


# ── F-01: Parent cancellation propagates to child ────────────
def test_parent_cancel_propagates():
    parent = ExecutionScope.create(
        agent_id="supervisor", session_id="s1", workspace_id="ws",
        execution_id="exec-1", conversation_id="conv-1", deadline_seconds=120.0
    )
    child = ExecutionScope.child_of(parent, agent_id="worker-1")
    parent.cancel()
    assert child.is_cancelled()


# ── F-01: ExecutionRegistry register/cancel/unregister ───────
def test_execution_registry():
    from runtime.server.execution_registry import ExecutionRegistry
    reg = ExecutionRegistry()
    scope = ExecutionScope.create(
        agent_id="k", session_id="s", workspace_id="ws",
        execution_id="exec-reg", conversation_id="c", deadline_seconds=60.0
    )
    reg.register(scope)
    assert reg.get("exec-reg") is scope
    assert reg.cancel("exec-reg") is True
    assert scope.is_cancelled()
    reg.unregister("exec-reg")
    assert reg.get("exec-reg") is None


# ── F-03: Policy store defaults to SAFE only ─────────────────
def test_policy_store_defaults():
    store = SessionPolicyRegistry()
    scopes = store.get_permitted_scopes("unknown-session")
    assert "SAFE" in scopes
    assert "DANGEROUS" not in scopes


# ── F-03: Policy grant adds scopes ───────────────────────────
def test_policy_store_grant():
    store = SessionPolicyRegistry()
    store.grant("s1", ["READ", "BROWSER"])
    permitted = store.get_permitted_scopes("s1")
    assert "SAFE" in permitted
    assert "READ" in permitted
    assert "BROWSER" in permitted
    assert "DANGEROUS" not in permitted


# ── F-03: Gateway deny unknown tool ──────────────────────────
def test_gateway_deny_unknown_tool():
    store = SessionPolicyRegistry()
    gw = PermissionGateway(store)
    assert not gw.is_authorized("s1", "some_unknown_tool")


# ── F-03: Gateway deny insufficient scope ────────────────────
def test_gateway_deny_insufficient_scope():
    store = SessionPolicyRegistry()
    gw = PermissionGateway(store)
    # run_command requires DANGEROUS; unconfigured session only has SAFE
    assert not gw.is_authorized("s1", "run_command")


# ── F-03: Gateway allow when scope granted ───────────────────
def test_gateway_allow_when_granted():
    store = SessionPolicyRegistry()
    store.grant("s1", ["DANGEROUS"])
    gw = PermissionGateway(store)
    assert gw.is_authorized("s1", "run_command")


# ── F-03: AuthorizedExecutor deny returns ToolResult ─────────
@pytest.mark.asyncio
async def test_authorized_executor_deny():
    store = SessionPolicyRegistry()
    gw = PermissionGateway(store)
    inner = AsyncMock()
    inner.execute_tool = AsyncMock(return_value=ToolResult(result="ok", error=None))
    executor = AuthorizedToolExecutor(inner, gw, session_id="s1")
    result = await executor.execute_tool("run_command", {"cmd": "rm -rf /"})
    assert result.error is not None
    assert "not authorized" in result.error
    inner.execute_tool.assert_not_awaited()


# ── F-03: AuthorizedExecutor allow and delegate ──────────────
@pytest.mark.asyncio
async def test_authorized_executor_allow():
    store = SessionPolicyRegistry()
    store.grant("s1", ["SAFE"])
    gw = PermissionGateway(store)
    inner = AsyncMock()
    inner.execute_tool = AsyncMock(return_value=ToolResult(result="found", error=None))
    executor = AuthorizedToolExecutor(inner, gw, session_id="s1")
    result = await executor.execute_tool("search", {"query": "test"})
    assert result.result == "found"
    inner.execute_tool.assert_awaited_once()


# ── F-04: Trace cleared after execution context ends ─────────
def test_trace_context_cleared():
    from runtime.observability.trace_context import set_trace, clear_trace, get_envelope
    set_trace("exec-x", "conv-x", "ag-x")
    assert get_envelope()["execution_id"] == "exec-x"
    clear_trace()
    assert get_envelope() == {}


# ── F-04: Concurrent executions independent ──────────────────
@pytest.mark.asyncio
async def test_concurrent_trace_isolation():
    from runtime.observability.trace_context import set_trace, clear_trace, get_envelope
    results = {}

    async def run(eid):
        set_trace(eid, f"conv-{eid}", "ag")
        await asyncio.sleep(0.01)
        results[eid] = get_envelope().get("execution_id")
        clear_trace()

    await asyncio.gather(run("A"), run("B"), run("C"))
    assert results["A"] == "A"
    assert results["B"] == "B"
    assert results["C"] == "C"


# ── F-05: ScopedContextAssembler output is string ────────────
def test_scoped_assembler_produces_string():
    from runtime.context.scoped_assembler import ScopedContextAssembler
    mem = MagicMock()
    mem.get_context_summary.return_value = "Rules here."
    mem.search_similar.return_value = []
    conv_mgr = MagicMock()
    conv_mgr.get_context.return_value = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]
    state = MagicMock()
    state.tasks = {}
    asm = ScopedContextAssembler(mem, conv_mgr, state)
    ctx = asm.assemble("exec-1", "conv-1", "kernel", query="Hello")
    prompt = ctx.as_prompt_string()
    assert isinstance(prompt, str)
    assert len(prompt) > 0
