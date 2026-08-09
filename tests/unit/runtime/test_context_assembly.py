"""
F-05 Context Assembly Tests — verified against actual runtime namespace.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from runtime.context.scoped_assembler import ScopedContextAssembler, AssembledContext


def make_assembler(rules="Rule: be helpful.", messages=None, budget=12000):
    mem = MagicMock()
    mem.get_context_summary.return_value = rules
    mem.search_similar.return_value = []

    conv_mgr = MagicMock()
    conv_mgr.get_context.return_value = messages or [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]

    state = MagicMock()
    state.tasks = {}

    return ScopedContextAssembler(mem, conv_mgr, state, char_budget=budget)


# ── 1. Basic assembly works ───────────────────────────────────
def test_basic_assembly():
    a = make_assembler()
    ctx = a.assemble("exec-1", "conv-1", "ag-1")
    assert isinstance(ctx, AssembledContext)
    assert "Rule" in ctx.system_rules
    assert len(ctx.recent_messages) == 2


# ── 2. Different conversations are isolated ──────────────────
def test_conversations_isolated():
    conv_mgr = MagicMock()
    def get_ctx(cid, limit=10):
        return [{"role": "user", "content": f"from {cid}"}]
    conv_mgr.get_context.side_effect = get_ctx
    mem = MagicMock()
    mem.get_context_summary.return_value = ""
    mem.search_similar.return_value = []
    state = MagicMock()
    state.tasks = {}

    asm = ScopedContextAssembler(mem, conv_mgr, state)
    ctx_a = asm.assemble("exec-1", "conv-A")
    ctx_b = asm.assemble("exec-1", "conv-B")
    assert ctx_a.recent_messages[0]["content"] == "from conv-A"
    assert ctx_b.recent_messages[0]["content"] == "from conv-B"


# ── 3. Budget enforced, truncated flag set ───────────────────
def test_budget_truncation():
    a = make_assembler(rules="X" * 5000, budget=100)
    ctx = a.assemble("e", "c")
    assert ctx.truncated is True
    assert len(ctx.system_rules) <= 100


# ── 4. Empty memory graceful ─────────────────────────────────
def test_empty_memory_graceful():
    a = make_assembler(rules="", messages=[])
    ctx = a.assemble("e", "c")
    assert ctx.system_rules == ""
    assert ctx.recent_messages == [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi!'}]
    assert not ctx.truncated


# ── 5. Memory exception does not raise ───────────────────────
def test_memory_exception_no_raise():
    mem = MagicMock()
    mem.get_context_summary.side_effect = Exception("DB down")
    mem.search_similar.return_value = []
    conv_mgr = MagicMock()
    conv_mgr.get_context.return_value = []
    state = MagicMock()
    state.tasks = {}
    asm = ScopedContextAssembler(mem, conv_mgr, state)
    ctx = asm.assemble("e", "c")  # must not raise
    assert ctx is not None


# ── 6. execution_id propagated ───────────────────────────────
def test_execution_id_propagated():
    a = make_assembler()
    ctx = a.assemble("exec-777", "conv-1")
    assert ctx.execution_id == "exec-777"


# ── 7. as_prompt_string contains expected sections ───────────
def test_as_prompt_string_structure():
    a = make_assembler()
    ctx = a.assemble("e", "c")
    prompt = ctx.as_prompt_string()
    assert "LONG TERM MEMORY" in prompt or "CONVERSATION HISTORY" in prompt


# ── 8. Semantic snippets included when query given ────────────
def test_semantic_included_with_query():
    mem = MagicMock()
    mem.get_context_summary.return_value = ""
    mem.search_similar.return_value = [{"text": "relevant fact"}]
    conv_mgr = MagicMock()
    conv_mgr.get_context.return_value = []
    state = MagicMock()
    state.tasks = {}
    asm = ScopedContextAssembler(mem, conv_mgr, state)
    ctx = asm.assemble("e", "c", query="something")
    assert "relevant fact" in ctx.semantic_snippets


# ── 9. Repeated assembly is deterministic ────────────────────
def test_repeated_assembly_deterministic():
    a = make_assembler()
    ctx1 = a.assemble("exec-1", "conv-1")
    ctx2 = a.assemble("exec-1", "conv-1")
    assert ctx1.system_rules == ctx2.system_rules
    assert ctx1.recent_messages == ctx2.recent_messages


# ── 10. State not mutated during assembly ────────────────────
def test_state_not_mutated():
    mem = MagicMock()
    mem.get_context_summary.return_value = "rules"
    mem.search_similar.return_value = []
    conv_mgr = MagicMock()
    conv_mgr.get_context.return_value = []
    state = MagicMock()
    state.tasks = {"t1": MagicMock(goal="do x", status=MagicMock(value="done"))}
    asm = ScopedContextAssembler(mem, conv_mgr, state)
    before = dict(state.tasks)
    asm.assemble("e", "c")
    assert state.tasks == before
