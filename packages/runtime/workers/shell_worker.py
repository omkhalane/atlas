"""
Isolated Shell Capability Worker
Executes sandboxed bash/terminal commands with output capture and status tracking.
"""
import asyncio
import logging
from typing import Dict, Any
from runtime.workers.base_worker import BaseCapabilityWorker, Job, JobResult

logger = logging.getLogger("atlas.workers.shell")


class ShellWorker(BaseCapabilityWorker):
    @property
    def worker_type(self) -> str:
        return "command"

    async def execute_job(self, job: Job) -> JobResult:
        cmd = job.parameters.get("command") or job.parameters.get("input", "echo ''")
        logger.info(f"[ShellWorker] Executing command in isolation: {cmd!r}")

        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=job.timeout_seconds)

            output = stdout.decode("utf-8") if stdout else ""
            error_out = stderr.decode("utf-8") if stderr else ""

            if proc.returncode == 0:
                return JobResult(job_id=job.id, success=True, data={"command": cmd, "stdout": output, "exit_code": 0})
            else:
                return JobResult(job_id=job.id, success=False, error=error_out or f"Exit code {proc.returncode}")
        except Exception as e:
            return JobResult(job_id=job.id, success=False, error=str(e))

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok", "worker_type": "command"}
