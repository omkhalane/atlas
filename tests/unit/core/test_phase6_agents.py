import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.python.agents.core_types.scope import ExecutionScope
from core.python.contracts.orchestration import AgentResult, AgentTaskNode
from core.python.contracts.tool import ToolResult
from core.python.agents.orchestration.supervisor import Supervisor
from core.python.agents.core_agents.react import ReActAgent
from core.python.agents.core_agents.plan_and_execute import PlanAndExecuteAgent

# Mock Provider
class MockProvider:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        
    async def generate(self, messages):
        res = self.responses[self.call_count]
        self.call_count += 1
        return res
        
# Mock Tool Executor
class MockToolExecutor:
    async def execute_tool(self, name, args):
        if name == "unauthorized":
            return ToolResult(result="", error="Not authorized")
        return ToolResult(result=f"Executed {name}", error=None)

# Mock Planner
class MockPlanner:
    async def generate_plan(self, goal, context):
        if goal == "empty":
            return "intent", [], False
        if goal == "fail":
            raise ValueError("Planning failed")
        return "intent", [AgentTaskNode(action="test", id="1")], False

# Mock Dispatcher
class MockDispatcher:
    async def execute_graph(self, task_id, graph):
        if not graph:
            return AgentResult(success=False, error="empty graph")
        return AgentResult(success=True, data=["ok"])

@pytest.mark.asyncio
async def test_react_final_answer():
    provider = MockProvider(["Thought: I know this.\nFinal Answer: 42"])
    tools = MockToolExecutor()
    agent = ReActAgent(provider, tools)
    scope = ExecutionScope.create(agent_id="react", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    res = await agent.run("goal", "context", scope)
    assert res.success is True
    assert res.data == "42"

@pytest.mark.asyncio
async def test_react_tool_then_answer():
    provider = MockProvider([
        'Thought: I need to search.\nAction: search\nAction Input: {"q": "test"}',
        'Thought: I have it.\nFinal Answer: found it'
    ])
    tools = MockToolExecutor()
    agent = ReActAgent(provider, tools)
    scope = ExecutionScope.create(agent_id="react", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    res = await agent.run("goal", "context", scope)
    assert res.success is True
    assert res.data == "found it"

@pytest.mark.asyncio
async def test_react_unauthorized_tool():
    provider = MockProvider([
        'Thought: I will run an unauthorized tool.\nAction: unauthorized\nAction Input: {}',
        'Thought: It failed.\nFinal Answer: could not execute'
    ])
    tools = MockToolExecutor()
    agent = ReActAgent(provider, tools)
    scope = ExecutionScope.create(agent_id="react", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    res = await agent.run("goal", "context", scope)
    assert res.success is True
    assert res.data == "could not execute"

@pytest.mark.asyncio
async def test_react_max_iterations():
    provider = MockProvider([
        'Thought: Looping.\nAction: search\nAction Input: {}'
    ] * 12)
    tools = MockToolExecutor()
    agent = ReActAgent(provider, tools)
    scope = ExecutionScope.create(agent_id="react", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    res = await agent.run("goal", "context", scope)
    assert res.success is False
    assert "Max iterations reached" in res.error

@pytest.mark.asyncio
async def test_react_cancellation():
    provider = MockProvider(['Thought: wait\nAction: search\nAction Input: {}'])
    tools = MockToolExecutor()
    agent = ReActAgent(provider, tools)
    scope = ExecutionScope.create(agent_id="react", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    scope.cancel()
    
    from core.python.agents.core_types.errors import ExecutionCancelledError
    with pytest.raises(ExecutionCancelledError):
        await agent.run("goal", "context", scope)

@pytest.mark.asyncio
async def test_plan_and_execute_success():
    agent = PlanAndExecuteAgent(MockPlanner(), MockDispatcher())
    scope = ExecutionScope.create(agent_id="plan", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    res = await agent.run("goal", "context", scope, "t1")
    assert res.success is True
    assert res.data == ["ok"]

@pytest.mark.asyncio
async def test_plan_and_execute_empty():
    agent = PlanAndExecuteAgent(MockPlanner(), MockDispatcher())
    scope = ExecutionScope.create(agent_id="plan", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    res = await agent.run("empty", "context", scope, "t1")
    assert res.success is False
    assert "empty graph" in res.error

@pytest.mark.asyncio
async def test_supervisor_routing():
    provider = MockProvider(["Thought: Hi\nFinal Answer: hello"])
    tools = MockToolExecutor()
    planner = MockPlanner()
    dispatcher = MockDispatcher()
    
    sup = Supervisor(provider, tools, planner, dispatcher)
    scope = ExecutionScope.create(agent_id="sup", session_id="s1", workspace_id="w1", execution_id="e1", conversation_id="c1", deadline_seconds=30.0)
    
    # Simple goal -> ReAct
    res1 = await sup.execute_task("t1", "simple goal", "context", scope)
    assert res1.success is True
    assert res1.data == "hello"
    
    # Complex goal -> Plan-and-execute
    res2 = await sup.execute_task("t2", "complex step-by-step plan", "context", scope)
    assert res2.success is True
    assert res2.data == ["ok"]

