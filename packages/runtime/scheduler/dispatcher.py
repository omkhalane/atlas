"""
Worker Job Dispatcher
Routes jobs from AIRuntime to isolated CapabilityWorker instances.
"""
import logging
from typing import Dict, Optional, Any
from runtime.workers.base_worker import BaseCapabilityWorker, Job, JobResult
from runtime.workers.browser_worker import BrowserWorker
from runtime.workers.filesystem_worker import FilesystemWorker
from runtime.workers.shell_worker import ShellWorker

logger = logging.getLogger("atlas.dispatcher")


class JobDispatcher:
    def __init__(self):
        self._workers: Dict[str, BaseCapabilityWorker] = {}
        self._register_default_workers()

    def _register_default_workers(self):
        self.register_worker("browser", BrowserWorker())
        self.register_worker("filesystem", FilesystemWorker())
        self.register_worker("command", ShellWorker())

    def register_worker(self, worker_type: str, worker: BaseCapabilityWorker):
        self._workers[worker_type] = worker
        logger.info(f"Registered capability worker: {worker_type}")

    async def dispatch(self, job: Job) -> JobResult:
        worker = self._workers.get(job.capability_id)
        if not worker:
            # Fallback to shell worker or error
            worker = self._workers.get("command")
            if not worker:
                return JobResult(job_id=job.id, success=False, error=f"No worker available for capability: {job.capability_id}")

        logger.info(f"[Dispatcher] Dispatching job {job.id} to worker {worker.worker_type}")
        return await worker.execute_job(job)
