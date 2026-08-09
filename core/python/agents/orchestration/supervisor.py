"""
Supervisor Agent
Routes execution to specialized worker agents based on task complexity.
"""
import logging
from core.python.agents.core_types.scope import ExecutionScope
from core.python.contracts.provider import IProviderManager
from core.python.contracts.tool import IToolExecutor
from core.python.contracts.orchestration import IExecutionDispatcher, IAgentPlanner, AgentResult
from core.python.agents.core_types.policy import AuthorizationManager

logger = logging.getLogger("atlas.supervisor")

class Supervisor:
    def __init__(
        self,
        provider: IProviderManager,
        tool_executor: IToolExecutor,
        planner: IAgentPlanner,
        dispatcher: IExecutionDispatcher,
        auth_manager: AuthorizationManager = None,
    ):
        self.provider = provider
        self.tool_executor = tool_executor
        self.planner = planner
        self.dispatcher = dispatcher
        self.auth_manager = auth_manager

    async def execute_task(self, task_id: str, goal: str, context: str, scope: ExecutionScope) -> AgentResult:
        logger.info(f"Supervisor evaluating goal: {goal}")
        
        # Heuristics
        goal_lower = goal.lower()
        is_complex = any(word in goal_lower for word in ["plan", "step-by-step", "complex", "graph", "multi"])
        is_code = any(word in goal_lower for word in ["code", "file", "read", "write", "refactor", "function"])
        is_browser = any(word in goal_lower for word in ["browser", "web", "navigate", "url", "search", "click"])
        
        if is_complex:
            logger.info("Supervisor routing to Plan-and-Execute worker")
            worker_scope = ExecutionScope.child_of(scope, agent_id="worker_plan_execute")
            from core.python.agents.core_agents.plan_and_execute import PlanAndExecuteAgent
            agent = PlanAndExecuteAgent(self.planner, self.dispatcher)
            res = await agent.run(goal, context, worker_scope, task_id)
        elif is_code:
            logger.info("Supervisor routing to Code worker")
            worker_scope = ExecutionScope.child_of(scope, agent_id="worker_code")
            from core.python.agents.core_agents.code_worker import CodeWorker
            agent = CodeWorker(self.provider, self.tool_executor)
            res = await agent.run(goal, context, worker_scope)
        elif is_browser:
            logger.info("Supervisor routing to Browser worker")
            worker_scope = ExecutionScope.child_of(scope, agent_id="worker_browser")
            from core.python.agents.core_agents.browser_worker import BrowserWorker
            agent = BrowserWorker(self.provider, self.tool_executor, self.auth_manager)
            res = await agent.run(goal, context, worker_scope)
        else:
            logger.info("Supervisor routing to ReAct worker")
            worker_scope = ExecutionScope.child_of(scope, agent_id="worker_react")
            from core.python.agents.core_agents.react import ReActAgent
            agent = ReActAgent(self.provider, self.tool_executor)
            res = await agent.run(goal, context, worker_scope)
            
        if not res.success:
            logger.error(f"Worker failed: {res.error}")
            
        return res
