import pytest
from runtime.llm.contracts import ExecutionContext, LLMMessage
from runtime.llm.context.sources import SystemSource, WorkspaceSource
from runtime.llm.context.token_budget import TokenBudgetManager
from runtime.llm.context.engine import ContextEngine


@pytest.mark.asyncio
async def test_context_engine_assembly():
    engine = ContextEngine()
    ctx = ExecutionContext()
    
    messages = await engine.build_context(ctx, "Hello world")
    assert len(messages) >= 2
    assert messages[-1].role == "user"
    assert messages[-1].content == "Hello world"


def test_token_budget_manager():
    manager = TokenBudgetManager(max_context_tokens=100, max_output_tokens=10)
    msg1 = LLMMessage(role="system", content="A" * 80)
    msg2 = LLMMessage(role="user", content="B" * 200)

    class DummySource:
        priority = 100

    fitted = manager.fit_to_budget([(DummySource(), [msg1, msg2])])
    assert len(fitted) <= 2
