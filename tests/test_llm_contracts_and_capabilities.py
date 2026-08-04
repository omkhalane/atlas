from runtime.llm.contracts import ExecutionContext, ProviderProfile, TaskPriority
from runtime.llm.capabilities import ProviderCapabilityRegistry, ModelCapability


def test_capability_registry_defaults():
    registry = ProviderCapabilityRegistry()
    
    cap = registry.get_capability("openai", "gpt-4o")
    assert cap.supports_vision is True
    assert cap.supports_prompt_caching is True
    assert cap.context_window == 128000

    cost = registry.calculate_cost("openai", "gpt-4o", 1000, 500)
    assert cost > 0.0


def test_execution_context():
    ctx = ExecutionContext(task_type="planner", priority=TaskPriority.PLANNER)
    assert ctx.priority == TaskPriority.PLANNER
    assert ctx.task_type == "planner"
    assert ctx.request_id is not None
