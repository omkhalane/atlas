import os
import shutil
import logging
from typing import Dict, List

logger = logging.getLogger("atlas.rollback")

class RollbackEngine:
    def __init__(self, backup_dir: str = "/code/ATLAS/.atlas/backups"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Maps task_id -> list of dicts {"path": original_path, "backup_path": backup_path, "action": "modified"|"deleted"|"created"}
        self._snapshots: Dict[str, List[dict]] = {}

    def snapshot_before_mutate(self, task_id: str, path: str):
        """Take a backup of a file before it's modified or deleted."""
        if not os.path.exists(path):
            # File is being created, rollback means deleting it
            self._add_record(task_id, path, None, "created")
            return
            
        if os.path.isdir(path):
            # Complex to snapshot entire directories, skip for MVP or use tar
            logger.warning(f"Snapshot for directory {path} not yet supported.")
            return

        backup_path = os.path.join(self.backup_dir, f"{task_id}_{os.path.basename(path)}")
        try:
            shutil.copy2(path, backup_path)
            self._add_record(task_id, path, backup_path, "modified")
            logger.info(f"Snapshot taken for {path} at {backup_path}")
        except Exception as e:
            logger.error(f"Failed to snapshot {path}: {e}")

    def _add_record(self, task_id: str, original_path: str, backup_path: str, action: str):
        if task_id not in self._snapshots:
            self._snapshots[task_id] = []
        self._snapshots[task_id].append({
            "path": original_path,
            "backup_path": backup_path,
            "action": action
        })

    def undo(self, task_id: str) -> bool:
        """Revert all filesystem changes made by a task."""
        if task_id not in self._snapshots:
            logger.info(f"No rollback records found for task {task_id}.")
            return False
            
        success = True
        records = self._snapshots[task_id]
        
        # Revert in reverse order
        for record in reversed(records):
            try:
                original = record["path"]
                backup = record["backup_path"]
                action = record["action"]
                
                if action == "created":
                    if os.path.exists(original):
                        os.remove(original)
                        logger.info(f"Rollback: deleted {original}")
                elif action == "modified":
                    if backup and os.path.exists(backup):
                        shutil.copy2(backup, original)
                        logger.info(f"Rollback: restored {original}")
                        os.remove(backup)
            except Exception as e:
                logger.error(f"Rollback failed for {record['path']}: {e}")
                success = False
                
        # Clear records after attempt
        del self._snapshots[task_id]
        return success
