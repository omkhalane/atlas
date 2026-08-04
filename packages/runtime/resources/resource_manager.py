"""
Resource Manager
Controls slot limits for local model sessions, active provider sockets, GPU memory, and file handles.
"""
import asyncio
import logging
from typing import Dict
from contextlib import asynccontextmanager

logger = logging.getLogger("atlas.resources")


class ResourceManager:
    def __init__(self):
        self._semaphores: Dict[str, asyncio.Semaphore] = {
            "local_llm_slots": asyncio.Semaphore(2),
            "cloud_provider_slots": asyncio.Semaphore(20),
            "browser_sessions": asyncio.Semaphore(3),
            "gpu_slots": asyncio.Semaphore(1)
        }

    @asynccontextmanager
    async def acquire(self, resource_type: str):
        sem = self._semaphores.get(resource_type)
        if sem:
            await sem.acquire()
            try:
                yield
            finally:
                sem.release()
        else:
            yield
