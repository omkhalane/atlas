import os
import json
import logging
from typing import List, Dict, Any
from runtime.kernel.task import ExecutionTask, TaskNode

logger = logging.getLogger("atlas.history")

class HistoryManager:
    def __init__(self, db_path: str = "/code/ATLAS/.atlas/history.jsonl"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            open(self.db_path, "a").close()

    def record_task(self, task: ExecutionTask):
        """Appends a completed task to the history ledger."""
        try:
            # We can't directly serialize Enum without a custom encoder, so we dump via model_dump_json
            task_json = task.model_dump_json()
            with open(self.db_path, "a") as f:
                f.write(task_json + "\n")
        except Exception as e:
            logger.error(f"Failed to record task history: {e}")

    def load_history(self, limit: int = 50) -> List[ExecutionTask]:
        """Loads recent tasks from history."""
        tasks = []
        try:
            with open(self.db_path, "r") as f:
                lines = f.readlines()
                # Read from the end
                for line in reversed(lines[-limit:]):
                    if line.strip():
                        tasks.append(ExecutionTask.model_validate_json(line))
        except Exception as e:
            logger.error(f"Failed to load task history: {e}")
        return tasks
