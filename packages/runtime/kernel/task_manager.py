import uuid
from typing import Optional
from runtime.kernel.state_manager import StateManager
from runtime.kernel.task import ExecutionTask, TaskStatus
from runtime.events.bus import EventBus

class TaskManager:
    def __init__(self, state_manager: StateManager, event_bus: EventBus):
        self.state = state_manager
        self.bus = event_bus

    async def create_task(self, goal: str, conversation_id: Optional[str] = None, task_id: Optional[str] = None) -> ExecutionTask:
        tid = task_id or str(uuid.uuid4())
        task = ExecutionTask(id=tid, goal=goal, conversation_id=conversation_id)
        self.state.add_task(task)
        
        await self.bus.publish("TASK_CREATED", {
            "task_id": tid,
            "goal": goal,
            "conversation_id": conversation_id
        })
        return task

    async def update_status(self, task_id: str, status: TaskStatus, error: Optional[str] = None):
        self.state.update_task_status(task_id, status, error)
        
        payload = {"task_id": task_id, "status": status.value}
        if error:
            payload["error"] = error
            
        await self.bus.publish("TASK_STATUS_CHANGED", payload)

    async def mark_done(self, task_id: str, artifacts: list = None):
        task = self.state.get_task(task_id)
        if task:
            if artifacts:
                task.artifacts.extend(artifacts)
            import time
            task.completed_at = time.time()
            
        await self.update_status(task_id, TaskStatus.DONE)
        
        await self.bus.publish("TASK_COMPLETED", {
            "task_id": task_id,
            "artifacts": task.artifacts if task else []
        })

    async def mark_failed(self, task_id: str, error: str):
        await self.update_status(task_id, TaskStatus.FAILED, error)
