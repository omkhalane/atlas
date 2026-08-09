"""
Core Orchestration Contracts
Defines minimal boundaries for Agent and Graph execution without importing runtime.
"""
from typing import Protocol, List, Any, Dict, Optional
import uuid

class AgentTaskNode:
    """Core domain equivalent of TaskNode."""
    def __init__(self, action: str, parameters: Dict[str, Any] = None, dependencies: List[str] = None, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.action = action
        self.parameters = parameters or {}
        self.dependencies = dependencies or []
        self.status = "created"
        self.result = None
        self.error = None

class AgentResult:
    """Result returned by any core agent."""
    def __init__(self, success: bool, data: Any = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error

class IExecutionDispatcher(Protocol):
    """
    Abstract execution dispatcher.
    Implemented by runtime to execute task graphs with infrastructure tracking.
    """
    async def execute_graph(self, task_id: str, graph: List[AgentTaskNode]) -> AgentResult:
        ...

class IAgentPlanner(Protocol):
    """
    Abstract planner interface.
    Generates a structured graph of tasks from a goal and context.
    """
    async def generate_plan(self, goal: str, context: str) -> tuple[str, List[AgentTaskNode], bool]:
        ...
