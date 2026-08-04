"""
Background Worker Pool
Async non-blocking task queue for background summaries, embeddings, memory updates, analytics.
"""
import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger("atlas.llm.background_worker")


class BackgroundWorkerPool:
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running: bool = False
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self):
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker_loop())
            logger.info("Background Worker Pool started.")

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

    def submit_task(self, func: Callable[..., Any], *args, **kwargs):
        self._queue.put_nowait((func, args, kwargs))

    async def _worker_loop(self):
        while self._running:
            try:
                func, args, kwargs = await self._queue.get()
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background task failed: {e}", exc_info=True)
