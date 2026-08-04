"""
Isolated Browser Capability Worker
Handles browser automation, Playwright scripts, DOM extraction, and page snapshots.
"""
import logging
from typing import Dict, Any
from runtime.workers.base_worker import BaseCapabilityWorker, Job, JobResult

logger = logging.getLogger("atlas.workers.browser")


class BrowserWorker(BaseCapabilityWorker):
    @property
    def worker_type(self) -> str:
        return "browser"

    async def execute_job(self, job: Job) -> JobResult:
        logger.info(f"[BrowserWorker] Executing job {job.id} for task {job.task_id} | action={job.action}")
        url = job.parameters.get("url") or job.parameters.get("input", "")
        # Mock/Isolated browser execution wrapper
        return JobResult(
            job_id=job.id,
            success=True,
            data={"action": job.action, "url": url, "status": "navigated", "title": "Browser Page"}
        )

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok", "worker_type": "browser"}
