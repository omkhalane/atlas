"""
Real System Integration Test Suite
Executes real tasks across Terminal, Filesystem, Browser, Search, and Memory capabilities.
"""
import os
import pytest
import asyncio
from runtime.ai_runtime import AIRuntime
from runtime.workers.base_worker import Job
from runtime.dag.execution_graph import ExecutionDAG, DAGNode
from runtime.kernel.task import TaskNode, ExecutionTask
from runtime.contracts import CapabilityRequest


@pytest.mark.asyncio
async def test_real_terminal_integration():
    """1. REAL Terminal Execution: Runs system diagnostic command."""
    ai = AIRuntime()
    await ai.start()

    job = Job(
        id="term_job_001",
        task_id="real_task_terminal",
        capability_id="command",
        action="run",
        parameters={"command": "python3 --version && uname -s"}
    )
    result = await ai.dispatcher.dispatch(job)

    assert result.success is True
    assert "Python 3" in result.data["stdout"]
    assert "Linux" in result.data["stdout"]
    print(f"\n[REAL TERMINAL TEST RESULT]:\nstdout: {result.data['stdout'].strip()}")
    await ai.shutdown()


@pytest.mark.asyncio
async def test_real_filesystem_integration(tmp_path):
    """2. REAL Filesystem Execution: Writes and reads a real file."""
    ai = AIRuntime()
    await ai.start()

    test_file = tmp_path / "atlas_real_test.txt"

    # Write file
    write_job = Job(
        id="fs_write_001",
        task_id="real_task_fs",
        capability_id="filesystem",
        action="write",
        parameters={"path": str(test_file), "content": "Atlas Real Systems Integration Test — SUCCESS\n"}
    )
    write_res = await ai.dispatcher.dispatch(write_job)
    assert write_res.success is True

    # Read file
    read_job = Job(
        id="fs_read_001",
        task_id="real_task_fs",
        capability_id="filesystem",
        action="read",
        parameters={"path": str(test_file)}
    )
    read_res = await ai.dispatcher.dispatch(read_job)
    assert read_res.success is True
    assert "Atlas Real Systems Integration Test" in read_res.data["content"]
    print(f"\n[REAL FILESYSTEM TEST RESULT]:\ncontent: {read_res.data['content'].strip()}")
    await ai.shutdown()


@pytest.mark.asyncio
async def test_real_browser_integration():
    """3. REAL Browser Capability Execution: Executes browser tab navigation script."""
    ai = AIRuntime()
    await ai.start()

    job = Job(
        id="browser_job_001",
        task_id="real_task_browser",
        capability_id="browser",
        action="run",
        parameters={"url": "https://news.ycombinator.com/", "script": "new_tab('https://news.ycombinator.com/')"}
    )
    result = await ai.dispatcher.dispatch(job)

    assert result.success is True
    assert result.data["status"] == "navigated"
    print(f"\n[REAL BROWSER TEST RESULT]:\ndata: {result.data}")
    await ai.shutdown()


@pytest.mark.asyncio
async def test_real_search_integration():
    """4. REAL Search Capability Execution: Performs ripgrep search in workspace."""
    ai = AIRuntime()
    await ai.start()

    from runtime.kernel.state_manager import StateManager
    from runtime.intelligence.memory import MemoryEngine
    from runtime.capabilities.search_port import SearchPort

    state = StateManager()
    mem = MemoryEngine()
    search_port = SearchPort(state)

    req = CapabilityRequest(id="search", parameters={"query": "AIRuntime", "domains": ["filesystem"]})
    res = search_port.execute(req)

    assert res.success is True
    assert "filesystem" in res.data
    print(f"\n[REAL SEARCH TEST RESULT]:\nmatches: {len(res.data['filesystem'])} lines found")
    await ai.shutdown()


@pytest.mark.asyncio
async def test_real_memory_integration():
    """5. REAL Memory Subsystem Execution: Stores and searches episodic/semantic memories."""
    ai = AIRuntime()
    await ai.start()

    from runtime.memory.episodic import Episode
    ep = Episode(id="task_mem_01", goal="Build Atlas Operating System", status="completed", outcome_summary="Architecture built successfully")
    ai.memory.episodic.record_episode(ep)
    ai.memory.semantic.store("Atlas AI OS handles browser, filesystem, terminal, and LLM sessions.", metadata={"category": "architecture"})

    similar = ai.memory.semantic.search("browser", top_k=1)
    assert len(similar) > 0
    assert "Atlas AI OS" in similar[0]["text"]

    fetched_ep = ai.memory.episodic.get_episode("task_mem_01")
    assert fetched_ep is not None
    assert fetched_ep.goal == "Build Atlas Operating System"

    print(f"\n[REAL MEMORY TEST RESULT]:\nfetched episode: {fetched_ep.goal} | status: {fetched_ep.status}")
    print(f"semantic search match: {similar[0]['text']}")
    await ai.shutdown()


@pytest.mark.asyncio
async def test_real_dag_execution_engine():
    """6. REAL End-to-End Execution Engine DAG Walker."""
    ai = AIRuntime()
    await ai.start()

    node1 = DAGNode(id="step_1", action="command", parameters={"action": "run", "command": "echo 'DAG Step 1 Complete'"})
    node2 = DAGNode(id="step_2", action="filesystem", parameters={"action": "create", "path": "/tmp/atlas_dag_test.tmp", "content": "DAG Execution OK"}, depends_on=["step_1"])

    dag = ExecutionDAG([node1, node2])
    results = await ai.execution_engine.run_dag("task_dag_real", dag)

    assert len(results) == 2
    task_events = ai.event_store.get_events_for_task("task_dag_real")
    assert len(task_events) >= 4  # TaskStarted, JobDispatched x2, NodeVerified x2, TaskFinished

    print(f"\n[REAL DAG EXECUTION TEST RESULT]:\nrecorded events: {[e.event_type for e in task_events]}")
    await ai.shutdown()
