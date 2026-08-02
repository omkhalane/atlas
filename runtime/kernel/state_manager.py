from typing import Dict, List, Optional
from runtime.kernel.task import ExecutionTask, TaskStatus

class StateManager:
    def __init__(self):
        self.tasks: Dict[str, ExecutionTask] = {}
        
    def add_task(self, task: ExecutionTask):
        self.tasks[task.id] = task
        
    def get_task(self, task_id: str) -> Optional[ExecutionTask]:
        return self.tasks.get(task_id)
        
    def update_task_status(self, task_id: str, status: TaskStatus, error: str = None):
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if error:
                self.tasks[task_id].error = error
                
    def get_tasks_by_conversation(self, conversation_id: str) -> List[ExecutionTask]:
        return [t for t in self.tasks.values() if t.conversation_id == conversation_id]
