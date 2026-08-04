import pytest
from runtime.ai_runtime import AIRuntime
from runtime.events.store import EventStore
from runtime.workers.base_worker import Job
from runtime.dag.execution_graph import ExecutionDAG, DAGNode
from runtime.execution.engine import ExecutionEngine
from runtime.scheduler.dispatcher import JobDispatcher
from runtime.policy.approval import ResumableApprovalManager


def test_event_store_append_and_replay():
    store = EventStore()
    evt = store.append("TaskStarted", task_id="task_test_001", payload={"nodes": 2})
    assert evt.event_id is not None
    assert evt.event_type == "TaskStarted"

    events = store.get_events_for_task("task_test_001")
    assert len(events) == 1
    assert events[0].task_id == "task_test_001"


@pytest.mark.asyncio
async def test_job_dispatcher_and_workers():
    dispatcher = JobDispatcher()
    job = Job(id="j1", task_id="t1", capability_id="command", action="run", parameters={"command": "echo 'Hello AI OS'"})
    
    result = await dispatcher.dispatch(job)
    assert result.success is True
    assert result.data["exit_code"] == 0


@pytest.mark.asyncio
async def test_execution_engine_with_event_store():
    event_store = EventStore()
    dispatcher = JobDispatcher()
    engine = ExecutionEngine(dispatcher, event_store)

    node1 = DAGNode(id="n1", action="command", parameters={"action": "run", "command": "echo 'Step 1'"})
    node2 = DAGNode(id="n2", action="filesystem", parameters={"action": "view", "path": "pyproject.toml"}, depends_on=["n1"])

    dag = ExecutionDAG([node1, node2])
    results = await engine.run_dag("task_dag_001", dag)

    assert len(results) == 2
    task_events = event_store.get_events_for_task("task_dag_001")
    assert len(task_events) >= 4  # TaskStarted, JobDispatched x2, NodeVerified x2, TaskFinished


def test_resumable_approval_manager():
    approval = ResumableApprovalManager()
    req = approval.request_approval("task_99", "file_delete", "User confirmation required")
    
    assert req.status == "pending"
    assert len(approval.get_pending_approvals()) == 1

    approved = approval.approve(req.id)
    assert approved is True
    assert req.status == "approved"
    assert len(approval.get_pending_approvals()) == 0
