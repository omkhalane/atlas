"""
Persistent Event Store — Event Sourcing Engine
Append-only event log capturing granular system events for auditing, time-travel, replay, and rollbacks.
"""
import os
import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("atlas.event_store")


@dataclass
class StoredEvent:
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    task_id: str = ""
    job_id: str = ""
    node_id: str = ""
    event_type: str = "GENERIC"     # "TaskStarted", "JobDispatched", "BrowserOpened", "ScreenshotCaptured", "NodeVerified", "TaskFinished", etc.
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EventStore:
    def __init__(self, log_dir: str = "/code/ATLAS/.atlas/events"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self._memory_log: List[StoredEvent] = []

    def append(self, event_type: str, task_id: str = "", job_id: str = "", node_id: str = "", payload: Dict[str, Any] = None) -> StoredEvent:
        event = StoredEvent(
            task_id=task_id,
            job_id=job_id,
            node_id=node_id,
            event_type=event_type,
            payload=payload or {}
        )
        self._memory_log.append(event)
        
        # Persist to append-only JSONL file per task
        filename = f"{task_id if task_id else 'system'}.jsonl"
        filepath = os.path.join(self.log_dir, filename)
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(event)) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist event {event.event_id}: {e}")

        logger.debug(f"[EventStore] {event.event_type} | task={task_id} | node={node_id}")
        return event

    def get_events_for_task(self, task_id: str) -> List[StoredEvent]:
        return [e for e in self._memory_log if e.task_id == task_id]

    def replay_task_events(self, task_id: str) -> List[StoredEvent]:
        filepath = os.path.join(self.log_dir, f"{task_id}.jsonl")
        events = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            events.append(StoredEvent(**data))
            except Exception as e:
                logger.error(f"Failed to replay events from file {filepath}: {e}")
        return events or self.get_events_for_task(task_id)
