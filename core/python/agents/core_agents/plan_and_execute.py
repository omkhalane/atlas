"""
Plan-and-Execute Agent
Deterministic executor for multi-step tasks.
"""
import logging
from core.python.agents.core_types.scope import ExecutionScope
from core.python.contracts.orchestration import IAgentPlanner, IExecutionDispatcher, AgentResult

logger = logging.getLogger("atlas.plan_and_execute")

class PlanAndExecuteAgent:
    def __init__(self, planner: IAgentPlanner, dispatcher: IExecutionDispatcher):
        self.planner = planner
        self.dispatcher = dispatcher

    async def run(self, goal: str, context: str, scope: ExecutionScope, task_id: str) -> AgentResult:
        scope.check_cancellation()
        
        max_replans = 3
        replans = 0
        current_context = context
        
        while replans < max_replans:
            # 1. Plan
            try:
                intent, graph, _ = await self.planner.generate_plan(goal, current_context)
                if not graph:
                    return AgentResult(success=False, error="Planner returned empty graph.")
            except Exception as e:
                return AgentResult(success=False, error=f"Planning failed: {e}")
                
            scope.check_cancellation()
            
            # 2. Execute via dispatcher
            try:
                result = await self.dispatcher.execute_graph(task_id, graph)
                if result.success:
                    return result
                
                # Dynamic replanning: if the graph failed, ask the planner for a new graph based on the error
                replans += 1
                logger.warning(f"Graph execution failed. Replanning ({replans}/{max_replans}). Error: {result.error}")
                current_context = context + f"\n\nPrevious Execution Error: {result.error}\nFailed Graph nodes: {[n.id for n in graph]}"
            except Exception as e:
                return AgentResult(success=False, error=f"Dispatcher failed: {e}")
                
        return AgentResult(success=False, error=f"Max replans ({max_replans}) reached without success.")
