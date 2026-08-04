"""
Recovery Manager
Saves state checkpoints and allows graceful resumption after unexpected failures.
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("atlas.recovery")


class RecoveryManager:
    def __init__(self, checkpoint_dir: str = "/code/ATLAS/.atlas/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, task_id: str, state_data: Dict[str, Any]):
        filepath = os.path.join(self.checkpoint_dir, f"{task_id}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2)
            logger.info(f"Saved checkpoint for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def load_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        filepath = os.path.join(self.checkpoint_dir, f"{task_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}")
        return None
