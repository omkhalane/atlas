"""
OS-Level Resource Manager
Tracks OS resources: GPU Memory, CPU %, RAM, Browser Sessions, Token Budget, Open File Handles, Disk, Rate Limits, Network.
"""
import asyncio
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager

logger = logging.getLogger("atlas.resources.os")


class OSResourceManager:
    def __init__(self):
        self._semaphores: Dict[str, asyncio.Semaphore] = {
            "gpu_memory": asyncio.Semaphore(1),
            "cpu_slots": asyncio.Semaphore(8),
            "ram_slots": asyncio.Semaphore(16),
            "browser_sessions": asyncio.Semaphore(3),
            "token_budget": asyncio.Semaphore(50),
            "file_handles": asyncio.Semaphore(100),
            "network_sockets": asyncio.Semaphore(30)
        }

    @asynccontextmanager
    async def acquire_resource(self, resource: str):
        sem = self._semaphores.get(resource)
        if sem:
            await sem.acquire()
            try:
                yield
            finally:
                sem.release()
        else:
            yield

    def get_resource_usage(self) -> Dict[str, Any]:
        return {
            res: sem._value for res, sem in self._semaphores.items()
        }
