from pydantic import BaseModel
from typing import List, Optional

class Verification(BaseModel):
    passed: bool
    checks: List[str]

class TaskResult(BaseModel):
    task_id: str
    status: str
    goal: str
    duration_ms: int
    capabilities_used: List[str]
    verification: Verification
    artifacts: List[str] = []
    requires_human: bool = False

class Task(BaseModel):
    id: str
    goal: str
