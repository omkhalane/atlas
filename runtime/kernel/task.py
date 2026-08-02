import uuid
import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.CREATED
    result: Optional[Any] = None
    error: Optional[str] = None

class ExecutionTask(BaseModel):
    id: str
    goal: str
    conversation_id: Optional[str] = None
    status: TaskStatus = TaskStatus.CREATED
    context: Dict[str, Any] = Field(default_factory=dict)
    graph: List[TaskNode] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    needs_cloud_reasoning: bool = False
    created_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    error: Optional[str] = None
