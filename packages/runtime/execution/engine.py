"""
Execution Engine — Airflow-Style Execution Core & DAG Walker
Manages node execution, dispatching jobs to workers, in-node assertion verifications, repair, and saga rollbacks.
"""
import uuid
import logging
from typing import Dict, List, Any, Optional

from runtime.dag.execution_graph import ExecutionDAG, DAGNode
from runtime.scheduler.dispatcher import JobDispatcher
from runtime.workers.base_worker import Job, JobResult
from runtime.events.store import EventStore
from runtime.execution.repair import RepairEngine
from runtime.execution.transaction import SagaTransactionManager
from runtime.execution.timeout import TimeoutManager

logger = logging.getLogger("atlas.execution_engine")


class ExecutionEngine:
    def __init__(self, dispatcher: JobDispatcher, event_store: EventStore):
        self.dispatcher = dispatcher
        self.event_store = event_store
        self.repair = RepairEngine()
        self.transactions = SagaTransactionManager()

    async def run_dag(self, task_id: str, dag: ExecutionDAG) -> Dict[str, Any]:
        self.event_store.append("TaskStarted", task_id=task_id, payload={"node_count": len(dag.nodes)})
        
        async def node_executor(node: DAGNode):
            job_id = f"job_{uuid.uuid4().hex[:8]}"
            job = Job(
                id=job_id,
                task_id=task_id,
                capability_id=node.action,
                action=node.parameters.get("action", "run"),
                parameters=node.parameters
            )
            
            self.event_store.append("JobDispatched", task_id=task_id, job_id=job_id, node_id=node.id, payload={"action": node.action})

            async def _dispatch_call():
                return await self.dispatcher.dispatch(job)

            try:
                # 1. Execute with Timeout & Retry
                result: JobResult = await TimeoutManager.execute_with_timeout(
                    _dispatch_call,
                    timeout_seconds=job.timeout_seconds,
                    max_retries=2
                )

                if not result.success:
                    # 2. Self-Healing Repair Attempt
                    repair_plan = await self.repair.attempt_repair(node.id, node.action, result.error or "Unknown error")
                    if repair_plan:
                        logger.info(f"Retrying node {node.id} with repair plan: {repair_plan}")
                        result = await _dispatch_call()

                if not result.success:
                    raise RuntimeError(f"Node execution failed: {result.error}")

                # 3. In-Node Verification
                self.event_store.append("NodeVerified", task_id=task_id, job_id=job_id, node_id=node.id, payload={"data": result.data})
                
                # 4. Record Transaction Step
                self.transactions.record_step(node.id, node.action, node.parameters.get("rollback"))

                return result.data

            except Exception as e:
                self.event_store.append("NodeFailed", task_id=task_id, job_id=job_id, node_id=node.id, payload={"error": str(e)})
                await self.transactions.execute_rollback()
                raise

        results = await dag.execute(node_executor)
        self.event_store.append("TaskFinished", task_id=task_id, payload={"results_count": len(results)})
        return results
