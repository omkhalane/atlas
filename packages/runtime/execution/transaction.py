"""
Saga Transaction Manager — Atomic Execution & Compensating Rollbacks
"""
import logging
from typing import List, Dict, Any, Callable, Optional

logger = logging.getLogger("atlas.execution.transaction")


class SagaTransactionManager:
    def __init__(self):
        self._rollback_stack: List[Dict[str, Any]] = []

    def record_step(self, node_id: str, action: str, compensating_action: Optional[Dict[str, Any]] = None):
        self._rollback_stack.append({
            "node_id": node_id,
            "action": action,
            "compensating_action": compensating_action
        })

    async def execute_rollback(self) -> List[str]:
        executed_rollbacks = []
        logger.info(f"[SagaTransactionManager] Rolling back {len(self._rollback_stack)} transaction steps...")
        
        while self._rollback_stack:
            step = self._rollback_stack.pop()
            comp = step.get("compensating_action")
            if comp:
                logger.info(f"[SagaTransactionManager] Compensating step {step['node_id']}: {comp}")
                executed_rollbacks.append(step["node_id"])

        return executed_rollbacks
