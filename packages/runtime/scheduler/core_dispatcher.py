"""
Core Dispatcher Adapter
Adapts the runtime ExecutionScheduler to the core IExecutionDispatcher interface.
"""
import logging
from typing import List
from core.python.contracts.orchestration import IExecutionDispatcher, AgentTaskNode, AgentResult
from runtime.kernel.task import ExecutionTask, TaskNode, TaskStatus
from common.execution.scheduler import ExecutionScheduler

logger = logging.getLogger("atlas.scheduler.core_adapter")

class CoreExecutionDispatcher(IExecutionDispatcher):
    def __init__(self, scheduler: ExecutionScheduler):
        self._scheduler = scheduler

    async def execute_graph(self, task_id: str, graph: List[AgentTaskNode]) -> AgentResult:
        # Convert core AgentTaskNodes to runtime TaskNodes
        runtime_nodes = []
        for node in graph:
            runtime_nodes.append(TaskNode(
                id=node.id,
                action=node.action,
                parameters=node.parameters,
                dependencies=node.dependencies
            ))
            
        # Create a dummy ExecutionTask for the scheduler
        rt_task = ExecutionTask(id=task_id, goal="Delegated by Core", graph=runtime_nodes)
        
        try:
            await self._scheduler.execute_graph(rt_task)
            
            # Check for failures
            failures = [n for n in rt_task.graph if n.status == TaskStatus.FAILED]
            if failures:
                return AgentResult(success=False, error=f"Graph execution failed on nodes: {[n.id for n in failures]}")
                
            return AgentResult(success=True, data=[n.result for n in rt_task.graph if n.result is not None])
        except Exception as e:
            return AgentResult(success=False, error=str(e))
