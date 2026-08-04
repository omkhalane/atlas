import asyncio
import logging
import json
from typing import Dict, Any, List, TYPE_CHECKING
from runtime.kernel.task import ExecutionTask, TaskNode, TaskStatus
from runtime.contracts import CapabilityRequest
from runtime.events.bus import EventBus
from runtime.policy.policy import PolicyEngine
from runtime.contracts.security import PermissionRequest
from runtime.kernel.rollback import RollbackEngine

if TYPE_CHECKING:
    from runtime.capabilities.registry import CapabilityRegistry

logger = logging.getLogger("atlas.scheduler")

class ExecutionScheduler:
    def __init__(self, registry: 'CapabilityRegistry', bus: EventBus, policy: PolicyEngine, rollback: RollbackEngine):
        self.registry = registry
        self.bus = bus
        self.policy = policy
        self.rollback = rollback

    async def execute_graph(self, task: ExecutionTask) -> List[Any]:
        # Create events for dependencies
        node_events: Dict[str, asyncio.Event] = {node.id: asyncio.Event() for node in task.graph}
        artifacts = []
        
        async def run_node(node: TaskNode):
            # Wait for dependencies
            for dep_id in node.dependencies:
                if dep_id in node_events:
                    await node_events[dep_id].wait()
            
            node.status = TaskStatus.RUNNING
            await self.bus.publish("STEP_STARTED", {"task_id": task.id, "step_id": node.id, "action": node.action})
            
            # Snapshot before mutate
            if node.action == "filesystem":
                fs_action = node.parameters.get("action")
                if fs_action in ["write_file", "append_file", "delete_file"]:
                    path = node.parameters.get("path")
                    if path:
                        self.rollback.snapshot_before_mutate(task.id, path)
            
            # Execute
            req = CapabilityRequest(id=node.action, parameters=node.parameters)
            result = await self.registry.execute(node.action, req)
            
            if result.success:
                node.status = TaskStatus.DONE
                node.result = result.data
                await self.bus.publish("STEP_COMPLETED", {"task_id": task.id, "step_id": node.id, "result": result.data})
                
                # Side effects like file tracking
                if node.action == "filesystem" and "path" in result.data:
                    import os
                    await self.bus.publish("file_written", {"path": result.data["path"], "name": os.path.basename(result.data["path"])})
            else:
                node.status = TaskStatus.FAILED
                node.error = result.error
                await self.bus.publish("STEP_FAILED", {"task_id": task.id, "step_id": node.id, "error": result.error})
                
            # Signal dependent nodes (even on failure, though we might want to short-circuit if failure)
            node_events[node.id].set()

        # Launch all workers concurrently
        workers = [asyncio.create_task(run_node(node)) for node in task.graph]
        if workers:
            await asyncio.gather(*workers)
            
        return artifacts
