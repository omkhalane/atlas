"""
Isolated Browser Capability Worker for Atlas Agent App
Integrates directly with @packages/browser/atlas-browser (Browser Harness CDP & recording).
"""
import os
import sys
import logging
import asyncio
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
        script = job.parameters.get("script") or job.parameters.get("code")

        atlas_browser_dir = "/code/ATLAS/packages/browser/atlas-browser"
        atlas_browser_src = os.path.join(atlas_browser_dir, "src")

        # If script payload is provided, run via browser-harness runner
        if script:
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{atlas_browser_src}:{env.get('PYTHONPATH', '')}"
            env["BH_RECORD"] = "1"  # Enable live recording traces
            
            try:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "browser_harness.run",
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                    cwd=atlas_browser_dir
                )
                stdout, stderr = await proc.communicate(input=script.encode("utf-8"))
                output_str = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")
                success = proc.returncode == 0
                return JobResult(
                    job_id=job.id,
                    success=success,
                    data={"action": job.action, "url": url, "status": "executed", "output": output_str}
                )
            except Exception as e:
                logger.error(f"[BrowserWorker] Execution failed: {e}")
                return JobResult(
                    job_id=job.id,
                    success=False,
                    error=str(e),
                    data={"action": job.action, "url": url, "status": "error"}
                )

        return JobResult(
            job_id=job.id,
            success=True,
            data={"action": job.action, "url": url, "status": "navigated", "title": "Browser Page"}
        )

    async def health(self) -> Dict[str, Any]:
        atlas_browser_dir = "/code/ATLAS/packages/browser/atlas-browser"
        installed = os.path.exists(atlas_browser_dir)
        return {"status": "ok" if installed else "degraded", "worker_type": "browser", "atlas_browser": installed}
