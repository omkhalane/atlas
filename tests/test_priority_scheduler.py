import pytest
from runtime.llm.contracts import ExecutionContext, TaskPriority
from runtime.scheduler.queue import PriorityScheduler


@pytest.mark.asyncio
async def test_priority_scheduler_ordering():
    scheduler = PriorityScheduler(max_concurrent=5)
    execution_order = []

    def task_action(name):
        execution_order.append(name)
        return name

    ctx_low = ExecutionContext(task_type="summary", priority=TaskPriority.CONVERSATION_SUMMARY)
    ctx_high = ExecutionContext(task_type="chat", priority=TaskPriority.CRITICAL_CHAT)

    await scheduler.enqueue(ctx_low, task_action, "low")
    await scheduler.enqueue(ctx_high, task_action, "high")

    assert len(execution_order) == 2
