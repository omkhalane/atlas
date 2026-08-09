"""
Core Planner Wrapper
Adapts the concrete LocalPlanner into the core IAgentPlanner interface.
"""
from typing import List, Tuple, Any
from core.python.contracts.orchestration import IAgentPlanner, AgentTaskNode

class CorePlanner(IAgentPlanner):
    """Wraps the runtime planner (duck-typed or explicitly passed) to return Core domain nodes."""
    def __init__(self, runtime_planner: Any):
        self._planner = runtime_planner

    async def generate_plan(self, goal: str, context: str) -> Tuple[str, List[AgentTaskNode], bool]:
        # generate_plan in local_planner expects a combined context string
        # and returns (intent, graph[TaskNode], needs_cloud)
        combined = f"USER REQUEST: {goal}\n{context}"
        intent, runtime_nodes, needs_cloud = self._planner.generate_plan(combined)
        
        # Convert runtime TaskNodes to core AgentTaskNodes
        core_nodes = []
        for rn in runtime_nodes:
            core_nodes.append(AgentTaskNode(
                action=rn.action,
                parameters=rn.parameters,
                dependencies=rn.dependencies,
                id=rn.id
            ))
            
        return intent, core_nodes, needs_cloud
