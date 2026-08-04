"""
Abstract Base Capability Worker Interface
Each worker runs as an isolated execution unit consuming jobs from the scheduler/dispatcher.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Job:
    id: str
    task_id: str
    capability_id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 30.0


@dataclass
class JobResult:
    job_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None


class BaseCapabilityWorker(ABC):
    @property
    @abstractmethod
    def worker_type(self) -> str:
        """e.g. 'browser', 'filesystem', 'shell', 'python', 'memory', 'llm'."""
        pass

    @abstractmethod
    async def execute_job(self, job: Job) -> JobResult:
        """Executes the given job inside an isolated worker runtime."""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Health check for worker status."""
        pass
