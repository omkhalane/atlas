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
        
    def set(self, key: str, value: any):
        if not hasattr(self, '_kv'):
            self._kv = {}
        self._kv[key] = value
        
    def get(self, key: str) -> any:
        if not hasattr(self, '_kv'):
            self._kv = {}
        return self._kv.get(key)
        
    def delete(self, key: str):
        if hasattr(self, '_kv') and key in self._kv:
            del self._kv[key]
