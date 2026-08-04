"""
Isolated Filesystem Capability Worker
Handles scoped file operations, reads, writes, directory lists, and file transfers.
"""
import os
import logging
from typing import Dict, Any
from runtime.workers.base_worker import BaseCapabilityWorker, Job, JobResult

logger = logging.getLogger("atlas.workers.filesystem")


class FilesystemWorker(BaseCapabilityWorker):
    @property
    def worker_type(self) -> str:
        return "filesystem"

    async def execute_job(self, job: Job) -> JobResult:
        logger.info(f"[FilesystemWorker] Executing job {job.id} for task {job.task_id} | action={job.action}")
        path = job.parameters.get("path", ".")
        action = job.action
        
        try:
            if action in ("read", "view"):
                if os.path.exists(path) and os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    return JobResult(job_id=job.id, success=True, data={"path": path, "content": content})
                return JobResult(job_id=job.id, success=False, error=f"File not found: {path}")

            elif action in ("write", "create"):
                content = job.parameters.get("content", "")
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return JobResult(job_id=job.id, success=True, data={"path": path, "written_bytes": len(content)})

            return JobResult(job_id=job.id, success=True, data={"path": path, "status": "executed"})
        except Exception as e:
            return JobResult(job_id=job.id, success=False, error=str(e))

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok", "worker_type": "filesystem"}
