"""
Execution DAG Engine
Executes multi-step/multi-agent tasks as directed acyclic dependency graphs.
"""
import asyncio
import logging
from typing import Dict, List, Any, Callable
from dataclasses import dataclass, field

logger = logging.getLogger("atlas.dag")


@dataclass
class DAGNode:
    id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Any = None
    error: Any = None


class ExecutionDAG:
    def __init__(self, nodes: List[DAGNode]):
        self.nodes: Dict[str, DAGNode] = {n.id: n for n in nodes}

    async def execute(self, executor_func: Callable[[DAGNode], Any]) -> Dict[str, Any]:
        results = {}
        completed = set()

        while len(completed) < len(self.nodes):
            # Find nodes whose dependencies are satisfied
            ready_nodes = [
                n for n in self.nodes.values()
                if n.id not in completed and all(dep in completed for dep in n.depends_on)
            ]

            if not ready_nodes:
                if len(completed) < len(self.nodes):
                    raise RuntimeError("Circular dependency or unfulfilled requirement in DAG")
                break

            # Execute ready nodes in parallel
            async def _run_node(node: DAGNode):
                node.status = "executing"
                try:
                    res = await executor_func(node)
                    node.result = res
                    node.status = "completed"
                    results[node.id] = res
                    return node.id
                except Exception as e:
                    node.status = "failed"
                    node.error = str(e)
                    logger.error(f"DAG Node {node.id} failed: {e}")
                    raise

            tasks = [_run_node(n) for n in ready_nodes]
            finished_ids = await asyncio.gather(*tasks, return_exceptions=True)

            for item in finished_ids:
                if isinstance(item, str):
                    completed.add(item)

        return results
